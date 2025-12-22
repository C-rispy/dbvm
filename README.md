# DBVM — A Minimal Assembler and Virtual Machine

DBVM is a systems programming project focused on building a **instruction set architecture (ISA)**, a **two-pass assembler**, and a **virtual machine**.

The goal is not performance or completeness, but understanding how assembly code is translated into machine instructions and how those instructions are executed at runtime.

At its current stage, the project implements:

* a small, explicit **instruction set definition**
* a **two-pass assembler with label resolution**
* a **virtual machine (VM)** with dynamic dispatch
* a VM-friendly machine code format
* CALL/RET stack support

---

## Project Structure

```
.
├── architecture.py   # Instruction set architecture definition
├── assembler.py      # Two-pass assembler (.dasm → .dmx)
├── vm.py             # Virtual machine / bytecode executor
├── sample.dasm       # Example assembly program 
```

---

## Instruction Set Architecture (`architecture.py`)

The ISA is intentionally minimal and explicit.

Key properties:

* Fixed-width instructions (32-bit words)
* Opcode stored in the lowest byte
* Operands packed into higher bytes
* Small, fixed register file (`R0 ... R7`)
* Fixed-size RAM (256 words)

### Memory layout

Although RAM is physically a flat array of 256 words, it is **logically partitioned**:

| Address range | Purpose |
|--------------|---------|
| `0x00 .. 0xBF` (0–191) | Program code and general data |
| `0xC0 .. 0xFF` (192–255) | Call stack |

This split is enforced at runtime:

* `ldm` / `stm` may **not** access stack memory
* `call` / `ret` exclusively use the stack region
* The program length must be `< STACK_BASE`

This separation models real-world code/data/stack memory conventions.

---

## Instruction Semantics (Selected)

* **LDI**
  * Loads a signed 8-bit immediate (`-128 .. 127`)
  * Immediate values are two’s-complement encoded
* **ADD / SUB**
  * Arithmetic wraps modulo 256
* **JMP / JZ / JNZ / CALL**
  * Jump targets must be valid instruction addresses (`< len(program)`)
* **CALL**
  * Pushes `ip + 1` onto the stack
  * Stack grows downward
  * Errors on stack overflow
* **RET**
  * Pops return address from the stack
  * Errors on stack underflow
* **PRR / PRM**
  * Print register or memory contents in decimal

---

## Assembler (`assembler.py`)

The assembler translates `.dasm` assembly files into machine code suitable for execution by the DBVM virtual machine.

### Design highlights

* **Two-pass assembly**

  * **Pass 1:** Resolve labels to instruction addresses
  * **Pass 2:** Encode instructions using numeric operands
* **Label support**

  * Labels (`label:`) name instruction addresses
  * Inline labels (`label: INSTR`) are supported
* **Flexible syntax**

  * Commas are treated as whitespace  
    (`ADD R0,R1,R2` ≡ `ADD R0 R1 R2`)
* **Immediate handling**

  * Signed 8-bit immediates (`-128 .. 127`)
  * Two’s complement encoding
* **Fail-fast validation**

  * Invalid opcodes, registers, immediates, or unresolved symbols produce clear assembler errors

### Output format

* One instruction per line
* Zero-padded 8-digit hexadecimal
* Each line represents a full 32-bit instruction word

Example output:

```
00008803
00000104
02000107
```

---

## Assembly Grammar (`.dasm`)

This assembler accepts a small, intentionally strict assembly language. Anything outside this grammar is rejected with a clear error.

### General Rules
- Assembly files are plain UTF-8 text.
- Parsing is line-based: each line contains at most one label and/or one instruction.
- Whitespace is flexible: extra spaces and tabs are allowed.
- Comments are stripped before parsing and do not affect instruction addresses.

### Comments
- A comment starts with `#` and runs to the end of the line.
- Full-line comments and trailing comments are allowed.

Example:
```asm
# full line comment
ADD R1, R2, R3   # trailing comment
```

### Labels
- A label defines a symbolic name for an instruction address.
- Label names are case-sensitive.
- A label may not contain whitespace or `:`.
- At most one label per line is allowed.

Valid forms:
```asm
loop:
loop: ADD R1, R2, R3
```

Invalid forms:
```asm
a:b: ADD R1, R2, R3    # multiple labels
: ADD R1, R2, R3       # empty label
```

Whitespace around the colon is allowed:
```asm
loop : ADD R1, R2, R3
```

### Instructions
- Instructions consist of a mnemonic followed by zero or more operands.
- Operands are separated by commas or whitespace.
- Each line contains at most one instruction.

General form:
```
MNEMONIC arg1, arg2, arg3
```

Example:
```asm
ADD R0, R1, R2
```

### Registers
- Registers are named `R0` through `R7`.
- Any other register name is invalid.

Example:
```asm
MOV R1, R0
```

### Immediates
- Immediate values may be:
  - decimal (e.g. `42`, `-7`)
  - hexadecimal with `0x` prefix (e.g. `0xFF`)
- Signed immediates must fit in 8 bits (`-128 .. 127`).

Example:
```asm
LDI R0, -7
LDI R1, 0x7F
```

### Memory Addresses
- Memory addresses are unsigned integers in the range `0 .. 255`.
- Addresses may be decimal or hexadecimal.
- Stack memory (`>= STACK_BASE`) is inaccessible to `ldm/stm`

Example:
```asm
LDM R0, 10
STM 0x20, R1
```

### Labels as Operands
- Labels may be used wherever an instruction expects an address (e.g. jumps).
- All labels must be defined somewhere in the file.

Example:
```asm
JMP loop
JNZ R0, done
```

---

## Virtual Machine (`vm.py`)

The DBVM virtual machine executes assembled `.dmx` bytecode.

### VM design highlights

* **Fixed-size RAM** (256 words)
* **Variable number of registers**
* **Instruction pointer (`ip`)**
* **Dynamic dispatch by opcode**
* **Single-instruction execution (`step`)**
* **Explicit runtime validation**

### Execution model

* Instructions are fetched from RAM at `ip`
* Opcode and operands are decoded from the 32-bit word
* Opcode dispatch selects a bound handler method
* Control-flow instructions explicitly modify `ip`
* All other instructions advance `ip` by one
* `call/ret` manage a downward-growing call stack

### Output behavior

* `prr/prm` produce runtime output
* After execution, the VM prints register contents and a RAM dump
* Step tracing (`--step`) prints directly to standard output

### Error handling

Runtime errors (invalid opcode, memory out-of-bounds, infinite loops) raise a dedicated `VMError`, clearly separating VM faults from Python implementation bugs.

---

## Usage

### Assemble `.dasm -> .dmx`

```bash
python assembler.py sample.dasm s_out.dmx
```

With label table:

```bash
python assembler.py sample.dasm s_out.dmx --dump-symbols
```

### Run Virtual Machine

```bash
python vm.py s_out.dmx output.txt
```

With step tracing:
```bash
python vm.py s_out.dmx output.txt --step
```

With maximum step limit:
```bash
python vm.py s_out.dmx output.txt --max-steps 1000
```

## Possible Extensions

This project intentionally keeps scope limited. Natural next steps include:


* disassembler (`.dmx → .dasm`)
* better CLI parsing
* memory-mapped I/O
* instruction execution profiling
* unit tests and golden outputs
* improve modular arithmetic logic

---

## Motivation

This project exists to internalize how:

* instruction sets are designed
* assemblers resolve symbols and encode programs
* virtual machines execute bytecode safely
* compile-time and runtime responsibilities differ

It is a learning-focused systems project, not a production tool.

---

## License

MIT License
