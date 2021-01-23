#ifndef FLIPJUMP_DEFS_H
#define FLIPJUMP_DEFS_H


//


#define WIDTH64

#define OUT0 (WIDTH*4)
#define OUT1 (WIDTH*4 + 1)
#define IN_IP (5)
#define BIT_VALUE_INDEX (LOG_WIDTH + 1)






#ifdef WIDTH64
    #define cell uint64_t
    #define WIDTH 64u
    #define LOG_WIDTH 6u
    #define HTON htonll
    #define NTOH ntohll
#endif

#ifdef WIDTH32
    #define cell uint32_t
    #define WIDTH 32u
    #define LOG_WIDTH 5u
    #define HTON htonl
    #define NTOH ntohl
#endif

#ifdef WIDTH16
    #define cell uint16_t
    #define WIDTH 16u
    #define LOG_WIDTH 4u
    #define HTON htons
    #define NTOH ntohs
#endif

void outputBit(uint8_t& currOutput, uint8_t& outputSize, int value) {
    if (outputSize == 0) {
        currOutput = value;
        outputSize = 1;
    } else {
        currOutput = 2 * currOutput + value;
        if (++outputSize == 8) {
            putchar(currOutput);
            outputSize = 0;
        }
    }
}

cell inputBit(uint8_t& currInput, uint8_t& inputSize) {
    if (inputSize == 0) {
        currInput = getchar();
        inputSize = 8;
    }
    cell res = (currInput % 2) ? (1u << BIT_VALUE_INDEX) : 0;
    currInput /= 2;
    inputSize--;
    return res;
}


#endif //FLIPJUMP_DEFS_H
