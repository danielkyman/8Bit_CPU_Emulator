# LS-8 Microcomputer Spec v4.0

## Registers

8 general-purpose 8-bit numeric registers R0-R7.

* R5 is reserved as the interrupt mask (IM)
* R6 is reserved as the interrupt status (IS)
* R7 is reserved as the stack pointer (SP)

> These registers only hold values between 0-255. After performing math on
> registers in the emulator, bitwise-AND the result with 0xFF (255) to keep the
> register values in that range.


## Internal Registers

* `PC`: Program Counter, address of the currently executing instruction
* `IR`: Instruction Register, contains a copy of the currently executing instruction
* `MAR`: Memory Address Register, holds the memory address we're reading or writing
* `MDR`: Memory Data Register, holds the value to write or the value just read
* `FL`: Flags, see below


## Flags

The flags register `FL` holds the current flags status. These flags
can change based on the operands given to the `CMP` opcode.

The register is made up of 8 bits. If a particular bit is set, that flag is "true".

`FL` bits: `00000LGE`

* `L` Less-than: during a `CMP`, set to 1 if registerA is less than registerB,
  zero otherwise.
* `G` Greater-than: during a `CMP`, set to 1 if registerA is greater than
  registerB, zero otherwise.
* `E` Equal: during a `CMP`, set to 1 if registerA is equal to registerB, zero
  otherwise.


## Memory

The LS-8 has 8-bit addressing, so can address 256 bytes of RAM total.

Memory map:

```
      top of RAM
+-----------------------+
| FF  I7 vector         |    Interrupt vector table
| FE  I6 vector         |
| FD  I5 vector         |
| FC  I4 vector         |
| FB  I3 vector         |
| FA  I2 vector         |
| F9  I1 vector         |
| F8  I0 vector         |
| F7  Reserved          |
| F6  Reserved          |
| F5  Reserved          |
| F4  Key pressed       |    Holds the most recent key pressed on the keyboard
| F3  Start of Stack    |
| F2  [more stack]      |    Stack grows down
| ...                   |
| 01  [more program]    |
| 00  Program entry     |    Program loaded upward in memory starting at 0
+-----------------------+
    bottom of RAM
```

## Stack

The SP points at the value at the top of the stack (most recently pushed), or at
address `F4` if the stack is empty.

## Power on State

When the LS-8 is booted, the following steps occur:

* `R0`-`R6` are cleared to `0`.
* `R7` is set to `0xF4`.
* `PC` and `FL` registers are cleared to `0`.
* RAM is cleared to `0`.

Subsequently, the program can be loaded into RAM starting at address `0x00`.

## Execution Sequence

1. The instruction pointed to by the `PC` is fetched from RAM, decoded, and
   executed.
2. If the instruction does _not_ set the `PC` itself, the `PC` is advanced to
   point to the subsequent instruction.
3. If the CPU is not halted by a `HLT` instruction, go to step 1.

Some instructions set the PC directly. These are:

* CALL
* INT
* IRET
* JMP
* JNE
* JEQ
* JGT
* JGE
* JLT
* JLE
* RET

In these cases, the `PC` does not automatically advance to the next instruction,
since it was set explicitly.

## Instruction Layout

Meanings of the bits in the first byte of each instruction: `AABCDDDD`

* `AA` Number of operands for this opcode, 0-2
* `B` 1 if this is an ALU operation
* `C` 1 if this instruction sets the PC
* `DDDD` Instruction identifier

The number of operands `AA` is useful to know because the total number of bytes in any
instruction is the number of operands + 1 (for the opcode). This
allows you to know how far to advance the `PC` with each instruction.

It might also be useful to check the other bits in an emulator implementation, but
there are other ways to code it that don't do these checks.

## Instruction Set

Glossary:

* **immediate**: takes a constant integer value as an argument
* **register**: takes a register number as an argument

* `iiiiiiii`: 8-bit immediate value
* `00000rrr`: Register number
* `00000aaa`: Register number
* `00000bbb`: Register number

Machine code values shown in both binary and hexadecimal.

### ADD

*This is an instruction handled by the ALU.*

`ADD registerA registerB`

Add the value in two registers and store the result in registerA.

Machine code:
```
10100000 00000aaa 00000bbb
A0 0a 0b
```

### CALL register

`CALL register`

Calls a subroutine (function) at the address stored in the register.

1. The address of the ***instruction*** _directly after_ `CALL` is
   pushed onto the stack. This allows us to return to where we left off when the subroutine finishes executing.
2. The PC is set to the address stored in the given register. We jump to that location in RAM and execute the first instruction in the subroutine. The PC can move forward or backwards from its current location.

Machine code:
```
01010000 00000rrr
50 0r
```

### CMP

*This is an instruction handled by the ALU.*

`CMP registerA registerB`

Compare the values in two registers.

* If they are equal, set the Equal `E` flag to 1, otherwise set it to 0.

* If registerA is less than registerB, set the Less-than `L` flag to 1,
  otherwise set it to 0.

* If registerA is greater than registerB, set the Greater-than `G` flag
  to 1, otherwise set it to 0.

Machine code:
```
10100111 00000aaa 00000bbb
A7 0a 0b
```

### HLT

`HLT`

Halt the CPU (and exit the emulator).

Machine code:
```
00000001 
01
```

### JEQ

`JEQ register`

If `equal` flag is set (true), jump to the address stored in the given register.

Machine code:
```
01010101 00000rrr
55 0r
```

### JGE

`JGE register`

If `greater-than` flag or `equal` flag is set (true), jump to the address stored
in the given register.

```
01011010 00000rrr
5A 0r
```

### JMP

`JMP register`

Jump to the address stored in the given register.

Set the `PC` to the address stored in the given register.

Machine code:
```
01010100 00000rrr
54 0r
```

### JNE

`JNE register`

If `E` flag is clear (false, 0), jump to the address stored in the given
register.

Machine code:
```
01010110 00000rrr
56 0r
```

### LDI

`LDI register immediate`

Set the value of a register to an integer.

Machine code:
```
10000010 00000rrr iiiiiiii
82 0r ii
```

### MUL

*This is an instruction handled by the ALU.*

`MUL registerA registerB`

Multiply the values in two registers together and store the result in registerA.

Machine code:
```
10100010 00000aaa 00000bbb
A2 0a 0b
```

### POP

`POP register`

Pop the value at the top of the stack into the given register.

1. Copy the value from the address pointed to by `SP` to the given register.
2. Increment `SP`.

Machine code:
```
01000110 00000rrr
46 0r
```

### PRN

`PRN register` pseudo-instruction

Print numeric value stored in the given register.

Print to the console the decimal integer value that is stored in the given
register.

Machine code:
```
01000111 00000rrr
47 0r
```

### PUSH

`PUSH register`

Push the value in the given register on the stack.

1. Decrement the `SP`.
2. Copy the value in the given register to the address pointed to by
   `SP`.

Machine code:
```
01000101 00000rrr
45 0r
```

### RET

`RET`

Return from subroutine.

Pop the value from the top of the stack and store it in the `PC`.

Machine Code:
```
00010001
11
```
