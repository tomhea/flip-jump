# FlipJump

FlipJump is an Esoteric language, with just 1 operation: <br>
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
100;    // Just flip: the  F;  syntax use the address of the following memory address as the jump-address.  
        // It is identical to:  100;some_label
                         //     some_label:
        // It is also identical to:  100;$
100     // You can also omit the semicolon

;200    // Just jump: the  ;J  syntax looks for the 'temp' label and use it as the flip-address.
        // It is identical to:  temp;200
        //  If this label is not defined, using this syntax will result in assemble error (use of undefined label 'temp').
        //  Of course it still flips the bit referenced by the 'temp' label.
        
;       // you can also omit both the flip/jump addresses.
        // It is identical to:  temp;some_label
                        //      some_label:
```

### More syntax options

```c
..pad 4     // Fills the memory with 0's until it is 4-opcodes aligned.

[len]value  // Put len-memory-bits with the value of 'value'.

// The next two lines are identical to the 64-bit fj opcode 123;456
[64]123
[60+4]460-4     

x = 13      // Declare constants
y = x+4     

a:
x;a+y/2

// The assembly is initialized with one constant - w.
// It is the memory-width (w=64 for 2^64 memory-bits), and the bit-width of every flip/jump adddress.
// The standard library runlib.fj declates more constants based on w, such as dw=2*w.
```

### Execution loop
The flipjump cpu has a built-in width, and start executing from address 0.
It halts on a simple self-loop (jumps to itself, while not flipping itself).

There are variants of the cpu, lets assume the simplest form:
- The jump address is always w-aligned.
- The operation doesn't flip bits in itself.

```c
#define BAD_ALIGNMENT 1
#define SELF_FLIP 2
#define SUCCESS_FINISH 0

int fj8(u8 mem) {
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
Or in other words, can it do anything meaningfull?
It turns out that it can, And much more than you'd think.

## Memory - how can we implement variables?
A bit can be built using 1 fj operation. Specifically,  ```;0```  or  ```;dw```<br>
Here the magic happens. The flipjump operation inherently can't read. It also can't write.<br>
All it knows is to flip a bit, and then jump. but where to?

The flipjump hidden-power is exactly in this delicate point. It can jump to an already flipped address.<br>
In other words, it can execute an already modified code.<br>
I based the main standard library functions, and the implementation of variables, on this exact point.

Follow the next example:

```c
// Lets assume a 64 bits cpu, and that the label branch_target is evaluated to 0x400 (1<<10).
// Follow the {1}, {2} numbers to follow the execution flow.

    ;code_start // {0} code starts at address 0
    ;
temp:
    ;
    ;
code_start:

// {1} We can flip the address in the bit_a opcode by the branch_target address (0x400):
    bit_a+64+10;    // The +64 is to get to the 2nd word (the address word), and the +10 is to flip the bit corrospondig to 0x400.
// {2} If we jump to execute the opcode in bit_a, it will flip 'temp' and then jump to the address written in it. 
//      So it will jump to 0x400, which is branch_target.
    ;bit_a

try_second_bit:
// {4} We will flip the address in the bit_b opcode by 0x400:
    bit_b+64+10;
// {5} Now we jump to execute the opcode in bit_b. It will flip 'temp' and then jump to the address written in it. 
//      So it will jump to 0x480 (was 0x80 from the start), which is second_branch_target.
    ;bit_b


branch_target:          // This is address 0x400
    // {3} Now we get here, and then continue jumping.
    ;try_second_bit
second_branch_target:   // This is address 0x480
    // {6} Another jump.
    ;end


end:  ;end  // {7} The code will get here and then finish (self loop).

bit_a:  ;0
bit_b:  ;0x80
```

The same flip/jump combination on bit_a/bit_b did different things. <br>
We successfully jumped to different addresses depends on the value of the said bits.<br>
In that way, we can *read* the value of such a bit-variable.

This is very nice, but it only worked because we knew the address of branch_target in advance.<br>
We usually don't, but it does resolved during assemble time.<br>
That's why the assembly language provides the next operation:

### flip_by

```c
    //TODO explain
```


## Input / Output
The addresses \[dw, 2\*dw] are reserved for IO.

```c
    //TODO explain
```

That's why the standart library runlib.fj defines the next macro:



## Macros
Macros are used to make our life easier. much easier.<br>
We declare them once, and can use the as much as we want.

It is important to say that macros can call other macros, and there are no macro-depth bounds.

The syntax for defining macros is:

```c
.def macro_name [arg ..] : [temp_label ..]
    // Macro body
.end

.def self_loop : loop_label       // No args, one temp label
    loop_label:
    ;loop_label
.end
```

The syntax for using macros is:
```c
.macro_name [arg ...]

.self_loop
```


Follow the example below.

```c
dw = 2*w
dbit = w + #w

.def bit bin
    ;(bin ? dw : 0)
.end

.def not bit
    bit+dbit;
.end

.def not8 var
    .not var+0*dw
    .not var+1*dw
    .not var+2*dw
    .not var+3*dw
    .not var+4*dw
    .not var+5*dw
    .not var+6*dw
    .not var+7*dw
.end


    ;code_start
    ;
temp: 
    ;
    ;
code_start:
    .not8 byte
end: 
    ;end


byte:
    .bit 0
    .bit 0
    .bit 1
    .bit 0
    .bit 1
    .bit 0
    .bit 1
    .bit 0
```

## Repetitions

The not8 macro seemed a bit.. repetative? There must be a better way of writing it.<br>
Well, there is.<br>
The syntax for repetitions is:

```c
.rep n i macro_name [macro_arg ..]
```
It repeats the use of macro_name n-times, each time with (index) i=0, i=1 until i=n-1 in the last time.

The above macro could be shortened to:

```c
.def not8 var
    .rep 8 i not var+i*dw
.end
```

The byte decleration can be shortened as well:

```c
.def byte val
    .rep 8 i bit (val>>i)&1
.end

byte:  .byte 84
```


### Hello, World!

```c
.def startup
    ;code_start
  IO:
    ;0
  temp:
    ;
    ;
  code_start:
.end


.def output_bit bit
    IO + bit
.end
.def output ascii
    .rep 8 i output_bit ((ascii>>i)&1)
.end

.def end_loop : loop_label
    loop_label:
    ;loop_label
.end

    .startup
    
    .output 'H'
    .output 'e'
    .output 'l'
    .output 'l'
    .output 'o'
    .output ','
    .output ' '
    .output 'W'
    .output 'o'
    .output 'r'
    .output 'l'
    .output 'd'
    .output '!'
    
    .end_loop
```

The flipfump assembly supports a ```..string "Hello, World!"``` syntax for initializing a variable with a string value.<br>
Look at tests/hello_world.fj program using print_str macro (stl/iolib.fj) for more info.

Note that all of these macros are already implemented in the standard library:
- startup  in runlib.fj
- end_loop in bitlib.fj (loop)
- output   in iolib.fj

# How to run?

```bash
>>> fja.py hello.fj -o hello.blm --no-stl
>>> fji.py hello.blm
Hello, World!
```

- The first line will assemble your code with the standard library files (w=64 as bits default).
  - The --no-stl flag tells the assembler not to include the standard-library. It is not needed as we implemented the macros ourselves.
- The second line will run your code.

# Project Structure

src (assembler source files):
  - parser.py       - pythonic lex/yacc parser.
  - preprocessor.py - unwind all macros and reps.
  - assembler.py    - assembles the macroless fj file.
  - defs.py         - general classes/functions/constants.
  - blm.py          - general read/write .blm (bit-level-memory) files.
  - fja.py          - the FlipJump Assembler script.
  - fji.py          - the FlipJump Interpreter script.

stl (standard library files - macros):
  - runlib.fj   - constants and initialization macros.
  - bitlib.fj   - macros for manipulating bits.
  - veclib.fj   - macros for manipulating bit vectors (i.e. numbers).
  - mathlib.fj  - advanced math macros (mul/div).
  - iolib.fj    - input/output macros, number casting.
  - ptrlib.fj   - pointers, stack and functions.

tests (flipjump programs), for example:
  - calc.fj
  - func.fj
  
# Read More
You can also read the *conventions.txt* file, and even start reading the bitlib.fj standard library file.
