# FlipJump

FlipJump is an Esoteric language ([FlipJump esolangs page](https://esolangs.org/wiki/FlipJump)), with just 1 operation: <br>
- Flip a bit, then (unconditionally) jump. <br>
- The operation takes 2 memory words, then flips (inverts) the bit referenced by the first word, and jumps to the address referenced by the second word. <br>

This project is both a **Macro Assembler** and a **Standard Library** to the language.

## The flipjump assembly (The 1 opcode)

```c
// The flip-jump syntax:  F;j
100;200     // This opcode will flip the 100th bit in memory, and will jump to address 200.

a:          // You can declare labels
a;300
a+4;2*a-a   // Will flip the a+4th bit (will override the above opcode), and jump to label a (to the above opcode).

temp:   0;c
b:
c: 
    8;19
  
temp + 2*(b-temp) - 13/4 ; temp & 0x67 + 0b00110   
    // You can use the labels (will be resolved to numbers at assemble-time) and many operations to make the flip/jump addresses:
    //  Mathmatical:  +- */% ()  
    //  Logical:  &|^  operations
    //  Shifts  << >>
    //  C-like trinary operator  ?:
    //  Bit-width operator  #  (minimal number of bits needed to store this number.  #x == log2(x)+1).
    // Also you can use hexadecimal (0x) and binary (0b) numbers, and get the ascii value of chars ('A' == 0x41).

b+'A';b+0x41    // The flip and jump addresses are identical in this line.

c+('A' > 'B' ? 1 : 'B');temp+(1<<(c-b))   // Is equivalent to c+0x42;temp+1

;$+2*64     // $ is the address of the next operation.
            // In this case, $ == a_label
a_label:
```



### Syntax Suger  (F; &nbsp; F &nbsp; ;J &nbsp; ;)
In many cases you won't need to specify both addresses.

```c
100;    // Just flip: the  F;  syntax uses the address of the following memory address as the jump-address.  
        // It is identical to:  100;$
        // It is also identical to:  100;some_label
                              //     some_label:

;200    // Just jump: the  ;J  syntax fills the flip-address with 0.
        // It is identical to:  0;200
        //  Of course it still flips the first bit in memory.
        
;       // you can also omit both the flip/jump addresses.
        // It is identical to:  0;$
```

### More syntax options

```c
x = 13      // Declare constants
y = x+4     

a:
x;a+y/2     // Use constants/labels as numbers.

pad 4  // Fills the memory with 0's until it is 4-opcodes aligned (not in the basic syntax, but a very basic macro found in the standard library).

// The assembly is initialized with one constant - w.
// It is the memory-width (w=64 for 2^64 memory-bits), and the bit-width of every flip/jump adddress.
// The standard library runlib.fj declates more constants based on w, such as dw=2*w.
```

### Execution loop
The flipjump CPU has a built-in width, and starts executing from address 0.
It halts on a simple self-loop (jumps to itself, while not flipping itself).

There are variants of the CPU, lets assume the simplest form:
- The jump address is always w-aligned.
- The operation doesn't flip bits in itself.

```c
#define BAD_ALIGNMENT 1
#define SELF_FLIP 2
#define SUCCESS_FINISH 0

int fj8(u8* mem) {
    u8 ip = 0;

    while (true) {
        u8 f = mem[ip/8];
        u8 j = mem[ip/8+1];

        if (ip % 8)  
            return BAD_ALIGNMENT;
        if (f >= ip && f < ip+16) 
            return SELF_FLIP;
        if (...) {
            // handle IO  (will be explained next).
        }
        if (ip == j) 
            return SUCCESS_FINISH;

        mem[f/8] ^= 1<<(f%8);   // Flip
        ip = j;                 // Jump
    }
}
```

# But, why?
Or in other words, can it do anything meaningful?
It turns out that it can, And much more than you'd think.

## Memory - how can we implement variables?
A bit can be built using 1 fj operation. Specifically, with  ```;0```  or  ```;dw```<br>
Here the magic happens. The flipjump operation inherently can't read. It also can't write.<br>
All it knows is to flip a bit, and then jump. but where to?

The flipjump hidden-power lies exactly in this delicate point. It can jump to an already flipped address.<br>
In other words, it can execute an already modified code.<br>
I based the main standard library functions, and the implementation of variables, on this exact point.

Follow the next example:

```c
// Lets assume a 64 bits cpu, and that the label branch_target is evaluated to 0x400 (1<<10).
// Follow the {0}, {1}, ... {9} numbers to follow the execution flow.

    ;code_start // {0} code starts at address 0
    ;
    ;
    ;
code_start:

// {1} We can flip the address in the bit_a opcode by the branch_target address (0x400):
    bit_a+64+10;    // The +64 is to get to the 2nd word (the address word), and the +10 is to flip the bit corrospondig to 0x400.
// {2} If we jump to execute the opcode in bit_a, it will flip address 0 and then jump to the address written in it. 
//      So it will jump to 0x400, which is branch_target.
    ;bit_a

try_second_bit:
// {5} We will flip the address in the bit_b opcode by 0x400:
    bit_b+64+10;
// {6} Now we jump to execute the opcode in bit_b. It will flip address 0 and then jump to the address written in it. 
//      So it will jump to 0x480 (was 0x80 from the start), which is second_branch_target.
    ;bit_b


branch_target:          // This is address 0x400
    // {4} Now we get here, and then continue jumping.
    ;try_second_bit
second_branch_target:   // This is address 0x480
    // {8} Another jump.
    ;end


end:  ;end  // {9} The code will get here and then finish (self loop).

bit_a:  ;0      // {3} Jump to branch_target
bit_b:  ;0x80   // {7} Jump to second_branch_target
```

The same flip/jump combination on bit_a/bit_b did different things. <br>
We successfully jumped to different addresses depends on the value of the said bits.<br>
In that way, we can *read* the value of such a bit-variable.

This is very nice, but it only worked because we knew the address of branch_target in advance.<br>
We usually don't, but it is resolved during assemble time.<br>
That's why the assembly language provides the next operation:

### wflip

```c
    wflip a, b
// The Word-Flip op is a special fj op.
// It flip the bits in addresses [a, a+w) iff the corresponding bit in b (b's value) is set.

// For example, for a==0x100, b=0x740 (0b 0111 0100 0000), the next blocks do the same thing:

    wflip a, b
    
    wflip 0x100, 0x740
    
    a+6;
    a+8;
    a+9;
    a+10;
    
    0x106;
    0x108;
    0x109;
    0x10a;
    
// This op is very useful if you want to set the jumping-part of another fj opcode to some address (and we know that it's zeroed before).
    // just do:  wflip fj_op+w, jump_address
// Also - setting the jumping-part back to zero can be simply done by doing the same wflip again:
    // (because b xor b == 0).

// Note that the assembler might choose to unwrap the wflip op in more complicated ways, for optimization reasons.

// This is some way of doing it (has the advantage of knowing in advance that wflip takes 1 op-size in its local area):    
    0x106;next_flips
next_op:
    
    // Many ops between...
    // ...
    
next_flips:
    0x108;
    0x109;
    0x10a;next_op
```


## Input / Output
The addresses \[dw, 2\*dw) are reserved for IO.

### Output
Flipping the dw's   bit will output '0'.<br>
Flipping the dw+1's bit will output '1'.<br>

```c
// For an ascii output - every 8 bits will generate (an lsb-first) byte, or an ascii-char.
// The next code will output the letter 'T' (0b01010100):
    dw;
    dw;
    dw+1;
    dw;
    dw+1;
    dw;
    dw+1;
    dw;
```
    
    
### Input

The next input bit is always loaded at address 3\*w + #w (3w+log(w)+1), when needed.<br>
You can use this bit by jumping to a flip-jump opcode that contains it.<br>
The best way is to jump to ;dw.<br>

In that way - this bit will reflect either 0x0 or 0x80 in the jump-part of the flip-jump op.<br>
If we ```wflip dw+w, some_padded_address``` before the ;dw - the dw-flip-jump-op will make a jump to ```some_padded_address``` / ```some_padded_address+0x80```, based on the input, just like [here](#memory---how-can-we-implement-variables).

```c
// For example:

    wflip dw+w, padded_address  // we assume dw+w is 0.
    ;dw

pad 2
padded_address:
    ;handle_0
    ;handle_1

handle_0:
    wflip dw+w, padded_address  // we make sure dw+w stays 0.
    // do some 0's stuff

handle_1:
    wflip dw+w, padded_address  // we make sure dw+w stays 0.
    // do some 1's stuff
```

The runlib.fj standard library defines macros to make IO as simple as possible.


## Macros
Macros are used to make our life easier. much easier. We declare them once, and can use them as much as we want.

Using a macro is just as pasting its content at the used spot.

It is important to say that macros can use other macros, and there are no macro-depth bounds.

The syntax for defining macros is:

```c
def macro_name param1, param2, .. @ temp_label1, temp_label2, .. {
    // Macro body
}

// for example:
def self_loop @ loop_label {       // No args, one temp label
    loop_label:
    ;loop_label
}
```
The temp labels are being generated for every use of this macro.

The syntax for using macros is:
```c
macro_name arg1, arg2, ..

// for example:
self_loop
xor dst, src
```


Follow the example below.

```c
dw = 2*w
dbit = w + #w

def bit bin {
    ;(bin ? dw : 0)
}

def not bit {
    bit+dbit;
}

def not8 var {
    not var+0*dw
    not var+1*dw
    not var+2*dw
    not var+3*dw
    not var+4*dw
    not var+5*dw
    not var+6*dw
    not var+7*dw
}


    ;code_start
    ;
code_start:
    not8 byte
end: 
    ;end


byte:
    bit 0
    bit 0
    bit 1
    bit 0
    bit 1
    bit 0
    bit 1
    bit 0
```

## Repetitions

The not8 macro seemed a bit.. repetitive? There must be a better way of writing it.<br>
Well, there is.<br>
The syntax for repetitions is:

```c
rep(n, i) macro_name macro_arg1, macro_arg2, ..
```
It repeats the use of macro_name n-times, each time with (index) i=0, i=1 until i=n-1 in the last time.
*n* is an expression and may contain constants and labels of previous addresses.

The above macro could be shortened to:

```c
def not8 var {
    rep(8, i) not var+i*dw
}
```

The byte decleration can be shortened as well:

```c
def byte val {
    rep(8, i) bit (val>>i)&1
}

byte:  byte 84
```

## Segments

You can split your code into different segments in memory. 
Your code implicitly starts at address 0 (like an implicit ```segment 0```).

```c
// some code
segment 0x10000
// some other code, will start at address 0x10000
```

Moreover, you can reserve a spot for 0-bits, without taking space in the assembled file.
The .fjm file supports segment-length > data-length. In that case the rest of the memory will be filled with zeros.

```c
reserve 3*w    // reserves 3*w 0-bits.
```

Both ```segment``` and ```reserve``` must get w-aligned values.

## Hello, World!

A simple fj [hello-world](tests/hello_no-stl.fj) program, not using the standard library:

```c
def startup {
    ;code_start
  IO:
    ;0
  code_start:
}


def output_bit bit {
    IO + bit;
}
def output ascii {
    rep(8, i) output_bit ((ascii>>i)&1)
}

def end_loop @ loop_label {
    loop_label:
    ;loop_label
}

    startup
    
    output 'H'
    output 'e'
    output 'l'
    output 'l'
    output 'o'
    output ','
    output ' '
    output 'W'
    output 'o'
    output 'r'
    output 'l'
    output 'd'
    output '!'
    
    end_loop

```

The flipfump assembly supports a ```string "Hello, World!"``` syntax for initializing a variable with a string value (```string``` is defined in the standard library).<br>
Look at [tests/hello_world.fj](tests/hello_world.fj) program using print_str macro ([stl/iolib.fj](stl/iolib.fj)) for more info.

Note that all of these macros are already implemented in the standard library:
- startup  in runlib.fj
- end_loop in bitlib.fj (loop)
- output   in iolib.fj

# How to run?

```bash
>>> fja.py hello.fj -o hello.fjm --no-stl
>>> fji.py hello.fjm
Hello, World!
```

- The first line will assemble your code (w=64 as bits default).
  - The --no-stl flag tells the assembler not to include the standard library. It is not needed as we implemented the macros ourselves.
- The second line will run your code.

You can also use the faster (stable, but still in developement) cpp-based interpreter (under src/cpp_fji):

```bash
>>> fji hello.fjm
Hello, World!
```

# Project Structure

**src** (assembler + interpreter source files):
  - cpp_fji/        - the cpp interpreter (much faster, about 2Mfj/s).
  - riscv2fj/       - translates a riscv-executable to an equivalent fj code.
  - parser.py       - pythonic lex/yacc parser.
  - preprocessor.py - unwind all macros and reps.
  - assembler.py    - assembles the macroless fj file.
  - defs.py         - classes/functions/constants used throughout the project.
  - fjm.py          - read/write .fjm (flip-jump-memory) files.
  - fja.py          - the FlipJump Assembler script.
  - fji.py          - the FlipJump Interpreter script.

**stl** (standard library files - macros):
  - runlib.fj   - constants and initialization macros.
  - bitlib.fj   - macros for manipulating bits.
  - veclib.fj   - macros for manipulating bit vectors (i.e. numbers).
  - mathlib.fj  - advanced math macros (mul/div).
  - iolib.fj    - input/output macros, number casting.
  - ptrlib.fj   - pointers, stack and functions.

**tests** (flipjump programs), for example:
  - calc.fj     - command line 2 hex/dec calculator, ```a [+-*/%] b```.
  - func.fj     - performs function calls and operations on stack.
  
# Read More

A more detailed explanations and the specifications of the FlipJump assembly can be found in the [FlipJump esolangs page](https://esolangs.org/wiki/FlipJump).

Start by reading the [bitlib.fj](src/bitlib.fj) standard library file. That's where the flipjump magic begins.

You can also write and run programs for yourself! It is just [that](#how-to-run) easy :)
