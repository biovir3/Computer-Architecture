"""CPU functionality."""

import sys

# Reserved Reg Numbers

IM = 5
IS = 6
SP = 7

# Constant flags for Equal, Less Than, and Greater Than

fl_EQUAL   = 0b001
fl_LESS    = 0b010
fl_GREATER = 0b100

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ie = 1  # Interrupts
        self.pc = 0  # Program Counter
        self.fl = 0  # Flags

        self.halted = False

        self.ram = [0] * 256
        self.reg = [0] * 8
        self.reg[SP] = 0xf4

        # This is true if the Instruction sets the Program Counter
        self.set_pc = False

        self.branch_table = {
            # HLT LDI PRN
            #0b00000001: self.opp_HLT,
            #0b10000010: self.opp_LDI,
            #0b01000111: self.opp_PRN,
            #0b10100010: self.opp_MUL,
            # Sprint Challange Adding ALU Instructions
            # adding them per the LS8 Cheatsheet
            # May not implement all of them and those will be commented out

            0b10100000: self.alu_ADD,
            0b10100001: self.alu_SUB,
            0b10100010: self.alu_MUL,
            0b10100011: self.alu_DIV,
            0b10100100: self.alu_MOD,
            0b01100101: self.alu_INC,
            0b01100110: self.alu_DEC,
            0b10100111: self.alu_CMP,
            0b10101000: self.alu_AND,
            0b01101001: self.alu_NOT,
            0b10101010: self.alu_OR,
            0b10101011: self.alu_XOR,
            0b10101100: self.alu_SHL,
            0b10101101: self.alu_SHR,

            # Adding PC Mutators

            0b01010000: self.opp_CALL,
            0b00010001: self.opp_RET,
            # 0b01010010: self.opp_INT, # I am not implementing Interupts
            0b00010011: self.opp_IRET,
            0b01010100: self.opp_JMP,
            0b01010101: self.opp_JEQ,
            0b01010110: self.opp_JNE,
            0b01010111: self.opp_JGT,
            0b01011000: self.opp_JLT,
            0b01011001: self.opp_JLE,
            0b01011010: self.opp_JGE,

            # Adding Other

            0b00000000: self.opp_NOP,
            0b00000001: self.opp_HLT,
            0b10000010: self.opp_LDI,
            0b10000011: self.opp_LD,
            0b10000100: self.opp_ST,
            0b01000101: self.opp_PUSH,
            0b01000110: self.opp_POP,
            0b01000111: self.opp_PRN,
            0b01001000: self.opp_PRA,
        }

    def load(self, file):
        """Load a program into memory."""

        address = 0

        with open(file) as source:
            for line in source:
                code = line.split('#')
                opp = code[0].strip()
                if opp == '':
                    continue
                opcode = int(opp, 2)
                self.ram[address] = opcode
                address += 1

    def ram_read(self, memaddr):
        return self.ram[memaddr]

    def ram_write(self, memaddr, memdata):
        self.ram[memaddr] = memdata

    def push_stk(self, val):
        self.reg[SP] -= 1
        self.ram_write(val,self.reg[SP])

    def pop_stk(self, val):
        val = self.ram_read(self.reg[SP])
        self.reg[SP] += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "DIV":
            self.reg[reg_a] /= self.reg[reg_b]
        elif op == "MOD":
            self.reg[reg_a] = self.reg[rega] % self.reg[reg_b]

        elif op == "INC":
            self.reg[reg_a] += 1
        elif op == "DEC":
            self.reg[reg_a] -= 1

        elif op == "CMP":
            # We have to clear the compare flags before we set them
            self.fl &= 0x11111000
            if self.reg[reg_a] < self.reg[reg_b]:
                self.fl |= fl_LESS
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.fl |= fl_GREATER
            else:
                self.fl |= fl_EQUAL

        elif op == "AND":
            self.reg[reg_a] &= self.reg[reg_b]
        elif op == "NOT":
            self.reg[reg_a] =  not self.reg[reg_b]
        elif op == "OR":
            self.reg[reg_a] |= self.reg[reg_b]
        elif op == "XOR":
            self.reg[reg_a] ^= self.reg[reg_b]
        elif op == "SHL":
            self.reg[reg_a] <<= self.reg[reg_b]
        elif op == "SHR":
            self.reg[reg_a] >>= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        while not self.halted:

            #self.trace()
            ir = self.ram[self.pc]
            opp_a = self.ram_read(self.pc + 1)
            opp_b = self.ram_read(self.pc + 2)

            instruction_size = ((ir >> 6) & 0b11) + 1
            self.set_pc = ((ir >> 4) & 0b1) == 1

            if ir in self.branch_table:
                #print(ir)
                self.branch_table[ir](opp_a, opp_b)
            else:
                print('Exception Occurred')
            if not self.set_pc:
                self.pc += instruction_size

    # def opp_HLT(self, a, b):
    #     self.halted = True
    #
    # def opp_LDI(self, a, b):
    #     self.reg[a] = b
    #
    # def opp_PRN(self, a, b):
    #     print(self.reg[a])

    # ALU Operations Will branch from the op to ALU where ALU will call these
    # IF I had more time, I would have the CPU have a seperate ALU class to handle this

    def alu_ADD(self, a, b):
        self.alu("ADD", a, b)

    def alu_SUB(self, a, b):
        self.alu("SUB", a, b)

    def alu_MUL(self, a, b):
        self.alu("MUL", a, b)

    def alu_DIV(self, a, b):
        self.alu("DIV", a, b)

    def alu_MOD(self, a, b):
        self.alu("MOD", a, b)

    def alu_INC(self, a, b):
        self.alu("INC", a, b)

    def alu_DEC(self, a, b):
        self.alu("DEC", a, b)

    def alu_CMP(self, a, b):
        self.alu("CMP", a, b)

    def alu_AND(self, a, b):
        self.alu("AND", a, b)

    def alu_NOT(self, a, b):
        self.alu("NOT", a, b)

    def alu_OR(self, a, b):
        self.alu("OR", a, b)

    def alu_XOR(self, a, b):
        self.alu("XOR", a, b)

    def alu_SHL(self, a, b):
        self.alu("SHL", a, b)

    def alu_SHR(self, a, b):
        self.alu("SHR", a, b)

    # PC Mutators

    def opp_CALL(self, a, b):
        self.push_stk(self.pc + 2)
        self.pc = self.reg[a]

    def opp_RET(self, a, b):
        self.pc = self.pop_stk()

    # def opp_INT(self, a, b): # I am not implementing Interupts
    #    pass

    def opp_IRET(self, a, b):
        for i in range(6, -1, -1):
            self.reg[i] = self.pop_stk()
        self.fl = self.pop_stk()
        self.pc = self.pop_stk()

    def opp_JMP(self, a, b):
        self.pc = self.reg[a]

    def opp_JEQ(self, a, b):
        if self.fl & fl_EQUAL:
            self.pc = self.reg[a]
        else:
            self.set_pc = False

    def opp_JNE(self, a, b):
        if not (self.fl & fl_EQUAL):
            self.pc = self.reg[a]
        else:
            self.set_pc = False

    def opp_JGT(self, a, b):
        if self.fl & fl_GREATER:
            self.pc = self.reg[a]
        else:
            self.set_pc = False

    def opp_JLT(self, a, b):
        if self.fl & fl_LESS:
            self.pc = self.reg[a]
        else:
            self.set_pc = False

    def opp_JLE(self, a, b):
        if self.fl & fl_EQUAL or self.fl & fl.LESS:
            self.pc = self.reg[a]
        else:
            self.set_pc = False

    def opp_JGE(self, a, b):
        if self.fl & fl_EQUAL or self.fl & fl.GREATER:
            self.pc = self.reg[a]
        else:
            self.set_pc = False

    # Other Opperations

    def opp_NOP(self, a, b):
        pass

    def opp_HLT(self, a, b):
        self.halted = True

    def opp_LDI(self, a, b):
        self.reg[a] = b

    def opp_LD(self, a, b):
        self.reg[a] = self.ram_read[self.reg[b]]

    def opp_ST(self, a, b):
        self.ram_write(self.reg[b],self.reg[a])

    def opp_PUSH(self, a, b):
        self.push_stk(self.reg[a])

    def opp_POP(self, a, b):
        self.reg[a] = self.pop_stk()

    def opp_PRN(self, a, b):
        print(self.reg[a])

    def opp_PRA(self, a, b):
        print(chr(self.reg[a]), end='')
        sys.stdout.flush()
