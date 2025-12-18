NUM_REG = 8  # number of registers
RAM_LEN = 256  # number of words in RAM
SIZE_LIM = 256 # program size limit: 256 instructions
# MISSING: enforce instruction width (4B); do assert len(args) == 3 in Assembler.compile()

OPS = {
    "hlt": {"code": 0x1, "fmt": "---"}, # Halt program
    "nop": {"code": 0x2, "fmt": "---"}, # Do nothing
    "ldi": {"code": 0x3, "fmt": "rv-"}, # Load value (signed imm8) into register r
    "mov": {"code": 0x4, "fmt": "rr-"}, # Copy register
    "ldm": {"code": 0x5, "fmt": "ra-"}, # Load from memory[address] into r
    "stm": {"code": 0x6, "fmt": "ar-"}, # Store r into memory[address]
    "add": {"code": 0x7, "fmt": "rrr"}, # Add r1 and r2, save to r0
    "sub": {"code": 0x8, "fmt": "rrr"}, # Subtract r2 from r1, save to r0
    "eq": {"code": 0x9, "fmt": "rrr"}, # r0 = (r1==r2), which is either 1 or 0
    "lt": {"code": 0xA, "fmt": "rrr"}, # r0 = (r1<r2), either 1 or 0
    "jmp": {"code": 0xB, "fmt": "a--"}, # jump to address
    "jz": {"code": 0xC, "fmt": "ra-"}, # jump to address if r == 0
    "jnz": {"code": 0xD, "fmt": "ra-"}, # jump to address if r != 0
    "prr": {"code": 0xE, "fmt": "r--"}, # print register in decimal
    "prm": {"code": 0xF, "fmt": "a--"}, # print memory[address] in decimal
}