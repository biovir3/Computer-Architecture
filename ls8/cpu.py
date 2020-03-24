"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ie = 1 # Interrupts
        self.pc = 0 # Program Counter
        self.fl = 0  # Flags

        self.halted = False

        self.ram = [0] * 256
        self.reg = [0] * 8

        self.branch_table = {
            # HLT LDI PRN
            0b00000001: self.opp_HLT,
            0b10000010: self.opp_LDI,
            0b01000111: self.opp_PRN,
            0b10100010: self.opp_MUL,
        }

    def load(self, file):
        """Load a program into memory."""

        address = 0

        with open(file) as source:
            for line in source:
                code = line.split('#')
                opp = code[0].strip()
                if code == '':
                    continue

                self.ram[address] = int(opp,2)
                address += 1

    def ram_read(self, memaddr):
        return self.ram[memaddr]

    def ram_write(self, memaddr, memdata):
        self.ram[memaddr] = memdata

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
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

            if ir in self.branch_table:
                #print(ir)
                self.branch_table[ir](opp_a, opp_b)
            else:
                print('Exception Occurred')

            self.pc += instruction_size

    def opp_HLT(self, a, b):
        self.halted = True

    def opp_LDI(self, a, b):
        self.reg[a] = b

    def opp_PRN(self, a, b):
        print(self.reg[a])

    def opp_MUL(self, a, b):
        self.reg[a] *= self.reg[b]
