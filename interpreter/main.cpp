#include <iostream>
#include <fstream>
#include <vector>

#include "defs.h"


// TODO list:
//  - add option to execute from middle of word (e.g. from the 12th bit of an aligned word).
//  - read program from .fjc file, init memory, and use w-bit-word accordingly.


using namespace std;

void runFJ(char* codeFJ) {
    cell ip = 0, temp;
    vector<cell> code;
    ifstream file(codeFJ, ios::binary | ios::in);

    uint8_t currInput = 0, inputSize = 0;
    uint8_t currOutput = 0, outputSize = 0;

    while(!file.eof()) {
        file.read(reinterpret_cast<char *>(&temp), sizeof(temp));
        code.push_back(NTOH(temp));
    }

    while (!(code[ip] != ip && code[ip] != ip+1 && code[ip+1] == ip)) {     // while not direct loop
        if (ip+1 == IN_IP) {    // if going to read IN_IP, just set ip;
            ip = inputBit(currInput, inputSize);
            continue;
        }

        cell toFlip = code[ip];

        if (toFlip == OUT0 || toFlip == OUT1) {
            outputBit(currOutput, outputSize, toFlip == OUT1);
        } else {
            code[toFlip >> LOG_WIDTH] ^= 1u << (toFlip & (WIDTH - 1));    // flip
        }

        ip = code[ip + 1];
    }
}


int main(int argc, char* argv[]) {
    if (argc != 2) {
        cout << "One argument expected - path/to/code.fjc" << endl;
        return 1;
    }
    runFJ(argv[1]);
    return 0;
}
