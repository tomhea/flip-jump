#include "include/argparse/include/argparse/argparse.hpp"
#include "fjmReader.h"
#include <bit>

using namespace std;


template <class W, bool ZeroInit, u16 Aligned, bool NoNullJump,
        bool CountStats, bool AllowSelfModify, bool JumpBeforeFlip>
void run(ifstream& file, istream& input, ostream& output, u64 fileFlags) {
    Mem<W, ZeroInit, Aligned, NoNullJump> mem(file, input, output, fileFlags);

    W ip = 0, f, j;
    W w = sizeof(W)*8;

    RunStatistics stats;

    while (true) {
        if (ip % Aligned) { //  [[unlikely]]
            cerr << "Error: read from an unaligned address (ip=0x" << hex << ip << ")." << endl;
            exit(1);
        }

        f = mem.read_word(ip);
        if constexpr (!AllowSelfModify) {
            if (ip <= f && f < ip + 2*w) {
                cerr << "Error: op tried to flip itself (ip=0x" << hex << ip << ", flip=0x" << hex << f << "), while the AllowSelfModify flag is off." << endl;
                exit(1);
            }
        }

        if constexpr ( JumpBeforeFlip) mem.flip_bit(f, stats);
        j = mem.read_word_check_input(ip + w, stats);
        if constexpr (!JumpBeforeFlip) mem.flip_bit(f), stats;

        if (ip == j && !(ip <= f && f < ip + 2*w))
            break;
        if constexpr (NoNullJump) {
            if (j < 2*w) {
                cerr << "Error: jump to address " << hex << j << " (while NoNullJump flag is on)." << endl;
                exit(1);
            }
        }
        ip = j;

        if constexpr (CountStats) stats.count();
    }

    stats.stopTimer();
//    if constexpr (CountStats)
    stats.printStats();
}


void cpu(ifstream& file, bool silent, u64 runFlags) {
    //TODO use the silent and runFlags fields.

    u16 magic, w;
    u64 fileFlags;
    readTo(file, magic);
    if (magic != FJ_MAGIC) {
        cerr << "Error: bad magic code (0x" << hex << magic << ", should be 0x" << hex << FJ_MAGIC << ")." << endl;
        exit(1);
    }
    readTo(file, w);
    readTo(file, fileFlags);

    switch (w) {
        case 8:
            run<u8 , false, 2*8 , true,    true, true, true>(file, cin, cout, fileFlags); break;
        case 16:
            run<u16, false, 2*16, true,    true, true, true>(file, cin, cout, fileFlags); break;
        case 32:
            run<u32, false, 2*32, true,    true, true, true>(file, cin, cout, fileFlags); break;
        case 64:
            run<u64, false, 2*64, true,    true, true, true>(file, cin, cout, fileFlags); break;
        default:
            cerr << "Error: bad word-width (" << w << " not in {8, 16, 32, 64})." << endl;          exit(1);
    }
}


int main(int argc, char *argv[]) {
    argparse::ArgumentParser program("Flip Jump Interpreter");

    program.add_argument("file")
            .help("the flip-jump memory file.")
            .required();

    program.add_argument("-s", "--silent")
            .help("don't show run times")
            .default_value(false)
            .implicit_value(true);

    program.add_argument("-f", "--flags")
            .help("running flags")
            .action([](const string& value) { return stoi(value); });

    program.add_argument("-d", "--debug")
            .help("debugging file.");

    //TODO support breakpoints (-b, -B).

    try {
        program.parse_args(argc, argv);
    }
    catch (const runtime_error& err) {
        cerr << err.what() << endl;
        cerr << program;
        exit(1);
    }

    auto file_path = program.get<string>("file");
    auto silent = program.get<bool>("--silent");
    auto flags = program.is_used("--flags") ? program.get<u64>("--flags") : 0;

    ifstream file(file_path);
    if (file.fail()) {
        cerr << "Can't open file " << file_path << "." << endl;
        exit(1);
    }
    cpu(file, silent, flags);
    return 0;
}