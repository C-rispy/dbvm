import sys
from architecture import OPS, NUM_REG, OP_SHIFT

class Assembler:
    def __init__(self,program):
        self._program = program
        self._reg = ["R"+str(i) for i in range(NUM_REG)]
        instructions = self._get_instructions()
        compiled = [self._compile(instr) for instr in instructions]

    def _get_instructions(self):
        instructions = [ln.strip() for ln in self._program if ln]
        instructions = [ln for ln in instructions if not self._iscomment(ln)]

    def _compile(self,instr):
        tokens = instr.split()
        op_code = tokens[0]
        assert op_code in OPS, f"{op_code} is invalid for this assembler"
        args = tokens[1:] if len(tokens) > 0 else None
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
        return ln.startswith("#")
    
    def _emit____(self,args,code):
        return self._encode(code)

    def _emit_r__(self,args,code):
        arg0 = args[0]
        assert arg0 in self._reg, f"Register index out of range"
        r = self._reg.index(arg0)
        return self._encode(r, code)

    def _emit_a__(self,args,code):
        

    def _emit_rv_(self,args,code):
        pass

    def _emit_ra_(self,args,code):
        pass

    def _emit_ar_(self,args,code):
        pass

    def _emit_rrr(self,args,code):
        pass


def main():
    assert len(sys.argv) == 3, f"Usage format: {sys.argv[0]} input|- output|-"
    assert sys.argv[1].endswith(".dasm") or sys.argv[1] == '-', f"Wrong input format. Needs to be .dasm file"
    reader = open(sys.argv[1],"r") if sys.argv[1] != "-" else sys.stdin
    writer = open(sys.argv[2],"w") if sys.argv[2] != "-" else sys.stdout
    program = reader.readlines()
    assembler = Assembler(program)


if __name__ == '__main__':
    main()