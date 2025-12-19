import sys
from architecture import OPS, NUM_REG, OP_SHIFT, OP_MASK, RAM_LEN

class Assembler:
    def __init__(self):
        self._reg = ["R"+str(i) for i in range(NUM_REG)]

    def assemble(self,lines):
        instructions = self._get_instructions(lines) # from here on out, the comment are stripped

        self._labels = {}
        counter = 0
        for ln in instructions:

            if ln.endswith(":"):
                new_ln = ln.split(":")
                new_ln[0] = new_ln[0].strip()
                assert len(new_ln) <= 2, f"Too many labels in one line: {ln}"
                self._labels[new_ln[0]] = counter

            elif ":" in ln:
                new_ln = ln.split(":")
                new_ln[0] = new_ln[0].strip()
                assert len(new_ln) <= 2, f"Too many labels in one line: {ln}"

                self._labels[new_ln[0]] = counter
                counter += 1

            else:
                counter += 1

        compiled = []
        for instr in instructions:
            if instr.endswith(":"):
                continue
            elif ":" in instr:
                new_instr = instr.split(":")
                assert len(new_instr) <= 2, f"Too many labels in one instruction: {instr}" # not sttrictly necessary, but we want to have each pass debuggable on its own
                new_instr[1] = new_instr[1].strip()
                compiled.append(self._compile(new_instr[1]))
            else:
                compiled.append(self._compile(instr))

        return compiled

    def _get_instructions(self,lines):
        instructions = []
        for ln in lines:
            instr = self._iscomment(ln)
            if instr == "":
                continue
            instructions.append(instr)
        return instructions

    def _compile(self,instr):
        instr = instr.replace(","," ") # comma handling
        instr = instr.strip() # in case comma was at the end and there is now a trailing whitespace
        tokens = instr.split()
        op_code = tokens[0]
        
        assert op_code in OPS, f"{op_code} is invalid for this assembler"
        args = tokens[1:]

        for i,a in enumerate(args): # label handling
            if a in self._reg:
                continue
            if a in self._labels.keys():
                args[i] = str(self._labels[a]) # keep operands as strings so emitters can parse uniformly
                continue
            try:
                int(a,0) # see if it's an imm8 (int(a,0) works for decimal and hex)
                continue
            except ValueError:
                raise AssertionError(f"Unknown symbol/operand {a} in {instr}")

        fmt = OPS[op_code]['fmt']
        code = OPS[op_code]['code']

        method_name = "_emit_" + fmt
        assert hasattr(self,method_name), f"Method for compiling {op_code} not implemented yet!"
        method = getattr(self,method_name)
        return method(args,code)

    def _encode(self,*args):
        assert len(args) > 0, f"cannot encode nothing"
        result = 0
        for a in args:
            result <<= OP_SHIFT
            result |= a
        return result

    def _iscomment(self,ln):
        if "#" in ln:
            new_ln = ln.split("#", maxsplit = 1)
            new_ln[0] = new_ln[0].strip()
            return new_ln[0] # returns "" if line starts with "#"
        else:
            return ln.strip()
    
    def _emit____(self,args,code):
        return self._encode(code)

    def _emit_r__(self,args,code):
        assert len(args) == 1, f"Wrong number of args passed!"
        assert args[0] in self._reg, f"Register index out of range"
        r = self._reg.index(args[0])
        return self._encode(r, code)

    def _emit_a__(self,args,code):
        assert len(args) == 1, f"Wrong number of args passed!"
        a = int(args[0],0)
        assert a < RAM_LEN and a >= 0, f"Memory address out of range"
        return self._encode(a, code)
    
    def _emit_rr_(self,args,code):
        assert len(args) == 2, f"Wrong number of args passed!"
        assert args[0] in self._reg and args[1] in self._reg, f"Register index out of range"
        rd = self._reg.index(args[0])
        ra = self._reg.index(args[1])
        return self._encode(ra, rd, code)
        
    def _emit_rv_(self,args,code):
        assert len(args) == 2, f"Wrong number of args passed!"
        assert args[0] in self._reg, f"Register index out of range"
        r = self._reg.index(args[0])
        v = int(args[1],0)
        assert v <= 127 and v >= -128, f"Passed imm8 {v} is supposed to be between -128 and 127!"
        v = v & OP_MASK
        return self._encode(v, r, code)

    def _emit_ra_(self,args,code):
        assert len(args) == 2, f"Wrong number of args passed!"
        assert args[0] in self._reg, f"Register index out of range"
        r = self._reg.index(args[0])
        a = int(args[1],0)
        assert a < RAM_LEN and a >= 0, f"Memory address out of range"
        return self._encode(a, r, code)

    def _emit_ar_(self,args,code):
        assert len(args) == 2, f"Wrong number of args passed!"
        a = int(args[0],0)
        assert a < RAM_LEN and a >= 0, f"Memory address out of range"
        assert args[1] in self._reg, f"Register index out of range"
        r = self._reg.index(args[1])
        return self._encode(r, a, code)

    def _emit_rrr(self,args,code):
        assert len(args) == 3, f"Wrong number of args passed!"
        assert args[0] in self._reg and args[1] in self._reg and args[2] in self._reg, f"Register index out of range"
        rd = self._reg.index(args[0])
        ra = self._reg.index(args[1])
        rb = self._reg.index(args[2])
        return self._encode(rb, ra, rd, code)


def main():
    assert len(sys.argv) == 3, f"Usage format: {sys.argv[0]} input|- output|-"
    assert sys.argv[1].endswith(".dasm") or sys.argv[1] == '-', f"Wrong input format. Needs to be .dasm file"
    reader = open(sys.argv[1],"r") if sys.argv[1] != "-" else sys.stdin
    writer = open(sys.argv[2],"w") if sys.argv[2] != "-" else sys.stdout
    lines = reader.readlines()
    assembler = Assembler()
    program = assembler.assemble(lines)
    for instruction in program:
        print(f"{instruction & 0xFFFFFFFF:08x}", file=writer)


if __name__ == '__main__':
    main()