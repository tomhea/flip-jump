#include <iostream>
#include <fstream>
#include "include/parallel_hashmap/parallel_hashmap/phmap.h"
#include <bit>
#include <cstdint>
#include <utility>
#include <vector>
#include <chrono>
#include <exception>


using namespace std;
using phmap::parallel_flat_hash_map;

typedef uint8_t  u8;
typedef uint16_t u16;
typedef uint32_t u32;
typedef uint64_t u64;


#define FJ_MAGIC 0x4a46
#define ZERO_INIT_FLAG(flags) (flags>>0)&1
#define ALIGNED_FLAG(flags) (flags>>1)&3

#define readTo(file, var) file.read(reinterpret_cast<char*>(&var),sizeof(var))


struct Segment {
    u64 segmentStart, segmentLen, dataStart, dataLen;
};


class RunStatistics {
    chrono::time_point<chrono::high_resolution_clock> lastStart;
    u64 opCount;
    u64 totalTimeMilliSeconds;

public:

    RunStatistics() : opCount(0), totalTimeMilliSeconds(0) { startTimer(); }

    void count() {
        opCount++;
    }

    void startTimer() {
        lastStart = chrono::high_resolution_clock::now();
    }

    void stopTimer() {
        totalTimeMilliSeconds +=
                duration_cast<chrono::nanoseconds>(chrono::high_resolution_clock::now() - lastStart).count();
    }

    void printStats() const {
        cout << "Finished after " << setprecision(4) << totalTimeMilliSeconds/1000000000.0 << "s (" << opCount << " FJ ops executed).";
    }
};


template <class W, bool ZeroInit, u16 Aligned, bool NoNullJump>
class Mem {
    parallel_flat_hash_map<W, W> mem;
    vector<pair<W, W>> zeroSegments;
    istream& input;
    ostream& output;
    u8 outCurr, outLen, inCurr, inLen;
    static constexpr W w = sizeof(W) * 8;
    static constexpr W inBit = w == 8 ? 4 : (w == 16 ? 5 : (w == 32 ? 6 : 7));


    inline W getNotMappedWord(W addr, W wordAddr, W val=0) {
        if constexpr (ZeroInit) {
            mem[wordAddr] = val;
            return val;
        } else {
            //TODO maybe prefetch hot spots.
            for (const pair<W, W> zeroSeg : zeroSegments) {
                if (zeroSeg.first <= wordAddr && wordAddr < zeroSeg.second) {
                    mem[wordAddr] = val;
                    return val;
                }
            }
            cerr << "Error: read from an uninitialized address " << addr << "." << endl;
            exit(1);
        }
    }

public:
    Mem(ifstream& file, istream& input, ostream& output, u64 fileFlags = 0, u64 runFlags = 0, u64 zerosFillThreshold = 1024)
            : mem(), zeroSegments(), input(input), output(output), outCurr(0), outLen(0), inCurr(0), inLen(0) {
        static_assert(Aligned != 0 && ((Aligned-1) & (Aligned)) == 0);
        static_assert(is_same<W, u8>() || is_same<W, u16>() || is_same<W, u32>() || is_same<W, u64>());

        u64 segmentNum;
        readTo(file, segmentNum);

        vector<Segment> segments;
        u64 segmentStart, segmentLen, dataStart, dataLen;
        for (int i = 0; i < segmentNum; i++) {
            readTo(file, segmentStart);
            readTo(file, segmentLen);
            readTo(file, dataStart);
            readTo(file, dataLen);
            segments.push_back({segmentStart, segmentLen, dataStart, dataLen});
        }

        vector<W> data;
        W datum;
        while (!file.eof()) {
            readTo(file, datum);
            data.push_back(datum);
        }

//        vector<W> data(std::istreambuf_iterator<W>(file), std::istreambuf_iterator<W>());

//    istreambuf_iterator<W> isbStart(file);
//    istreambuf_iterator<W> isbStartData(isbStart + segmentNum*sizeof(Segment));
//    istreambuf_iterator<W> isbEnd;
//
//    vector<Segment> segments(isbStart, isbStartData);
//    vector<W> data(isbStartData, isbEnd);


        // Fill segments.
        for (const Segment& seg : segments) {
            for (u64 i = 0; i < seg.dataLen; i++)
                mem[seg.segmentStart + i] = data.at(seg.dataStart + i);
            if (seg.segmentLen < seg.dataLen) {
                cerr << "Error: segment-length is smaller than data-length:  " << seg.segmentLen << " < " << seg.dataLen << endl;
                exit(1);
            }
            if (seg.segmentLen > seg.dataLen) {
                u64 start = seg.segmentStart + seg.dataLen;
                u64 end = seg.segmentStart + seg.segmentLen;
                if (seg.segmentLen - seg.dataLen <= zerosFillThreshold) {
                    for (u64 i = start; i < end; i++)
                        mem[i] = 0;
                } else {
                    zeroSegments.push_back({start, end});
                }
            }
        }
    }


    inline W read_word_check_input(W addr, RunStatistics& stats) {
        W wordAddr = addr/(sizeof(W)*8);

        if (wordAddr < 4) {
            if (addr <= 3*w+inBit && 3*w+inBit < addr+w) {
                if (inLen == 0) {
                    stats.stopTimer();
                    inCurr = input.get();
                    stats.startTimer();
                    inLen = 8;
                }

                W is1 = inCurr & 1;
                if (!mem.modify_if(3, [is1](W& val) {
                    if (is1 ^ ((val>>inBit)&1))
                        val ^= 1 << inBit;
                })) {
                    getNotMappedWord(3*w+inBit, 3, is1 ? 1 << inBit : 0);
                }

                inLen--;
                inCurr>>=1;
            }
        }
        return read_word(addr);
    }


    inline W read_word(W addr) {
        W wordAddr = addr/(sizeof(W)*8), val;
        if (mem.if_contains_unsafe(wordAddr, [&val](W value) {val=value;}))
            return val;
        else
            return getNotMappedWord(addr, wordAddr);
    }



    inline void flip_bit(W addr, RunStatistics& stats) {
        if (addr <= 2*w+1 && addr >= 2*w) {
            if (addr == 2*w+1)
                outCurr |= 1<<outLen;
            if (++outLen == 8) {
                stats.stopTimer();
                output.put(outCurr);
                output.flush();
                stats.startTimer();
                outCurr = outLen = 0;
            }
        } else {
            W wordAddr = addr / w;
            W bitMask = 1 << (addr % w);
            if (!mem.modify_if(wordAddr, [bitMask](W& val) {val ^= bitMask;})) {
                getNotMappedWord(addr, wordAddr, bitMask);
            }
        }
    }
};


