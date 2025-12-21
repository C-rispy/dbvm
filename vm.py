import sys
from architecture import NUM_REG, OP_MASK, OP_SHIFT, OPS, RAM_LEN

COLUMNS = 4
class VirtualMachine:
    def __init__(self):
        self.initialize([])
        self._dispatch = {
            OPS[mnemonic]["code"]: getattr(self,"_op_" + mnemonic) for mnemonic in OPS.keys()
            if hasattr(self, "_op_" + mnemonic)
        }
    
    def initialize(self,program):
        self._program = program
        if len(self._program) >= RAM_LEN:
            raise VMError("Program is too long")
        self._ram = [
            program[i] if (i < len(self._program)) else 0
            for i in range(RAM_LEN)
        ]
        self._ip = 0
        self._reg = [0] * NUM_REG
    
    def step(self):
        if not (0 <= self._ip < RAM_LEN):
            raise VMError("Instruction pointer out of bounds", ip = self._ip)
        instr, op_code, arg0, arg1, arg2 = self._fetch()
        handler = self._dispatch.get(op_code)
        if handler is None:
            raise VMError(f"Invalid opcode 0x{op_code:02x}", ip = self._ip, instr = instr)
        ip_before = self._ip
        next_ip = ip_before + 1
        ret = handler(arg0, arg1, arg2)
        if ip_before == self._ip:
            self._ip = next_ip
        return ret

    def _fetch(self):
        instruction = self._ram[self._ip]
        op_code = instruction & OP_MASK
        instruction >>= OP_SHIFT
        arg0 = instruction & OP_MASK
        instruction >>= OP_SHIFT
        arg1 = instruction & OP_MASK
        instruction >>= OP_SHIFT
        arg2 = instruction & OP_MASK
        instr = self._ram[self._ip]
        return (instr, op_code, arg0, arg1, arg2)

    def run(self, *, max_steps=None, writer=sys.stdout):
        steps = 0
        try:
            while True:
                if max_steps is not None and steps >= max_steps:
                    raise VMError("Max steps exceeded: {max_steps}",ip = self._ip)
                halted = self.step()
                steps += 1
                if not halted:
                    return
        except VMError as e:
            print(f"VMError: {e}",file=writer)
            sys.exit(1)

    def show(self, writer):
        for i,r in enumerate(self._reg):
            print(f"R{i:0x} = {r:08x}",file = writer)
        max_ram = max(i for (i,m) in enumerate(self._ram) if m != 0)
        low = 0
        while low <= max_ram:
            output = f"{low:06x}: "
            for i in range(COLUMNS):
                output += f"  {self._ram[low + i]:06x}"
            print(output, file=writer)
            low += COLUMNS

    def _op_hlt(self,arg0,arg1,arg2):
        return False # halted = False -> return

    def _op_nop(self,arg0,arg1,arg2):
        return True # do nothing

    def _op_ldi(self,arg0,arg1,arg2):
        r = arg0
        v = arg1
        self._reg[r] = v
        return True

    def _op_mov(self,arg0,arg1,arg2):
        r1 = arg0
        r2 = arg1
        self._reg[r1] = self._reg[r2]
        return True

    def _op_ldm(self,arg0,arg1,arg2):
        r = arg0
        a = arg1
        self._reg[r] = self._ram[a]
        return True

    def _op_stm(self,arg0,arg1,arg2):
        a = arg0
        r = arg1
        self._ram[a] = self._reg[r]
        return True

    def _op_add(self,arg0,arg1,arg2):
        rd = arg0
        ra = arg1
        rb = arg2
        self._reg[rd] = self._reg[ra] + self._reg[rb]
        return True

    def _op_sub(self,arg0,arg1,arg2):
        rd = arg0
        ra = arg1
        rb = arg2
        self._reg[rd] = self._reg[ra] - self._reg[rb]
        return True

    def _op_eq(self,arg0,arg1,arg2):
        rd = arg0
        ra = arg1
        rb = arg2
        if self._reg[ra] == self._reg[rb]:
            self._reg[rd] = 1
        else:
            self._reg[rd] = 0
        return True

    def _op_lt(self,arg0,arg1,arg2):
        rd = arg0
        ra = arg1
        rb = arg2
        if self._reg[ra] < self._reg[rb]:
            self._reg[rd] = 1
        else:
            self._reg[rd] = 0
        return True

    def _op_jmp(self,arg0,arg1,arg2):
        a = arg0
        self._ip = a
        if a >= len(self._program):
            raise VMError("Jump address {a} invalid!",ip=self._ip)
        return True

    def _op_jz(self,arg0,arg1,arg2):
        r = arg0
        a = arg1
        if self._reg[r] == 0:
            self._ip = a
            if a >= len(self._program):
                raise VMError("Jump address {a} invalid!",ip=self._ip)
        return True

    def _op_jnz(self,arg0,arg1,arg2):
        r = arg0
        a = arg1
        if self._reg[r] != 0:
            self._ip = a
            if a >= len(self._program):
                raise VMError("Jump address {a} invalid!",ip=self._ip)
        return True

    def _op_prr(self,arg0,arg1,arg2):
        r = arg0
        print(self._reg[r])
        return True

    def _op_prm(self,arg0,arg1,arg2):
        a = arg0
        if a >= len(RAM_LEN):
            raise VMError("RAM address {a} invalid!",ip=self._ip)
        print(self._ram[a])
        return True

class VMError(RuntimeError):
    def __init__(self, msg, *, ip=None, instr=None):
        parts = [msg]
        if ip is not None:
            parts.append(f"ip={ip}")
        if instr is not None:
            parts.append(f"instr=0x{instr:08x}")
        super().__init__(" | ".join(parts))
        self.ip = ip
        self.instr = instr


def main():
    assert len(sys.argv) >= 3, f"Usage format: {sys.argv[0]} input|- output|- (--flag)"
    assert sys.argv[1].endswith(".dmx") or sys.argv[1] == '-', f"Wrong input format. Needs to be .dmx file"
    reader = open(sys.argv[1],"r") if sys.argv[1] != "-" else sys.stdin
    writer = open(sys.argv[2],"w") if sys.argv[2] != "-" else sys.stdout

    lines = [ln.strip() for ln in reader.readlines()]
    program = [int(ln,16) for ln in lines if ln]

    vm = VirtualMachine()
    vm.initialize(program)
    vm.run()
    vm.show(writer)

if __name__ == '__main__':
    main()