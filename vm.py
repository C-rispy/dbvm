import sys
from architecture import NUM_REG, OP_MASK, OP_SHIFT, OPS, RAM_LEN

class VirtualMachine:
    def __init__(self):
        self.initialize([])
        self._dispatch = {
            OPS[mnemonic]["code"]: getattr(self,"_op_" + mnemonic) for mnemonic in OPS.keys()
            if hasattr(self, "_op_" + mnemonic)
        }
    
    def initialize(self,program):
        if len(program) <= RAM_LEN:
            raise VMError("Program is too long")
        self._ram = [
            program[i] if (i < len(program)) else 0
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
                if halted:
                    return
        except VMError as e:
            print(f"VMError: {e}",file=writer)
            sys.exit(1)

    def show(writer):
        pass

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
    assert len(sys.argv) >= 3, f"Usage format: {sys.argv[0]} input|- output|- (flag)"
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