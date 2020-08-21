"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [None] * 256
        self.reg = [0] * 8
        self.FL = [0] * 8
        self.pc = 0
        self.LDI = 0b10000010
        self.HLT = 0b00000001
        self.PRN = 0b01000111
        self.MUL = 0b10100010
        self.PUSH = 0b01000101
        self.POP = 0b01000110
        self.CALL = 0b01010000
        self.RET = 0b00010001
        self.ADD = 0b10100000
        self.CMP = 0b10100111
        self.JMP = 0b01010100
        self.JEQ = 0b01010101
        self.JNE = 0b01010110
        self.instructions_table = {}
        self.instructions_table[self.LDI] = self.ldi
        self.instructions_table[self.PRN] = self.prn
        self.instructions_table[self.MUL] = self.mul
        self.instructions_table[self.ADD] = self.add
        self.instructions_table[self.PUSH] = self.push
        self.instructions_table[self.POP] = self.pop
        self.instructions_table[self.CALL] = self.call
        self.instructions_table[self.RET] = self.ret
        self.instructions_table[self.CMP] = self.compare
        self.instructions_table[self.JMP] = self.jump
        self.instructions_table[self.JEQ] = self.jump_if_equal
        self.instructions_table[self.JNE] = self.jump_if_not_equal
        self.sp = 0xF4
        self.reg[7] = self.sp
        pass

    def load(self):
        """Load a program into memory."""

        address = 0

        if len(sys.argv) < 2:
            print('ERROR - Provide program address to load')
            return

        program_filename = sys.argv[1]

        program_text = open(program_filename).read()
        program_lines = program_text.split('\n')
        program = []

        for line in program_lines:
            blocks = line.split()
            if len(blocks) > 0:
                if blocks[0] != '#':
                    inst = blocks[0]
                    program.append(int(inst, 2))

        for instruction in program:
            self.ram[address] = instruction
            address += 1

    def ram_read(self, add):
        return self.ram[add]

    def ram_write(self, add, value):
        self.ram[add] = value

    def ldi(self):
        add = self.ram[self.pc + 1]
        value = self.ram[self.pc + 2]
        self.reg[add] = value
        self.pc += 3

    def prn(self):
        add = self.ram[self.pc + 1]
        value = self.reg[add]
        print(value)
        self.pc += 2

    def mul(self):
        add1 = self.ram_read(self.pc + 1)
        add2 = self.ram_read(self.pc + 2)
        self.alu('MUL', add1, add2)
        self.pc += 3

    def add(self):
        add1 = self.ram_read(self.pc + 1)
        add2 = self.ram_read(self.pc + 2)
        self.alu('ADD', add1, add2)
        self.pc += 3

    def push(self):
        add = self.ram_read(self.pc + 1)
        self.sp -= 1
        self.ram[self.sp] = self.reg[add]
        self.pc += 2

    def pop(self):
        add = self.ram_read(self.pc + 1)
        self.reg[add] = self.ram[self.sp]
        self.sp += 1
        self.pc += 2

    def call(self):
        self.sp -= 1
        self.ram[self.sp] = self.pc + 2
        self.pc = self.reg[self.ram[self.pc + 1]]

    def jump(self):
        self.pc = self.reg[self.ram[self.pc + 1]]

    def ret(self):
        self.pc = self.ram[self.sp]
        self.sp += 1

    def compare(self):
        add1 = self.ram_read(self.pc + 1)
        add2 = self.ram_read(self.pc + 2)
        self.alu('CMP', add1, add2)
        self.pc += 3

    def jump_if_equal(self):
        add = self.reg[self.ram[self.pc + 1]]
        if self.FL[7]:
            self.pc = add
        else:
            self.pc += 2

    def jump_if_not_equal(self):
        add = self.reg[self.ram[self.pc + 1]]
        if self.FL[5] or self.FL[6]:
            self.pc = add
        else:
            self.pc += 2

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "CMP":
            if self.reg[reg_a] == self.reg[reg_b]:
                self.FL[7] = 1
                self.FL[5] = 0
                self.FL[6] = 0
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.FL[6] = 1
                self.FL[5] = 0
                self.FL[7] = 0
            else:
                self.FL[5] = 1
                self.FL[6] = 0
                self.FL[7] = 0
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        inst = None

        running = True

        while running:
            inst = self.ram[self.pc]

            if inst in self.instructions_table:
                self.instructions_table[inst]()
            elif inst == self.HLT:
                running = False
            else:
                self.pc += 1
