# DBVM — A Minimal Assembler and Instruction Set

DBVM is a systems programming project focused on building a **simple instruction set architecture (ISA)**, a **two-pass assembler** and a **virtual machine**.

The goal is not performance or completeness, but conceptual clarity: understanding how assembly code is translated into machine instructions.

At its current stage, the project implements:

* a small, explicit **instruction set definition**
* a **two-pass assembler with label resolution**
* a deterministic, VM-friendly machine code output format

A virtual machine / executor is planned but **not yet implemented**.

---

## Project Structure

```
.
├── architecture.py   # Instruction set architecture definition
├── assembler.py      # Two-pass assembler
```

---

## Instruction Set Architecture (`architecture.py`)

The ISA is intentionally minimal and explicit.

Key properties:

* **Fixed-width instructions** (32-bit words)
* **Opcode in the lowest byte**
* Operands packed into higher bytes
* Small, fixed register file (`R0 ... R{N-1}`)
* Byte-addressed RAM with bounded size

Instruction encodings, operand formats, and constants are defined centrally in `architecture.py`, and are consumed by the assembler.

---

## Assembler (`assembler.py`)

The assembler translates `.dasm` assembly files into machine code suitable for execution by a future virtual machine.

### Design highlights

* **Two-pass assembly**

  * **Pass 1:** Resolve labels to instruction addresses (program counter values)
  * **Pass 2:** Encode instructions using numeric operands
* **Label support**

  * Labels (`label:`) name instruction addresses
  * Labels are resolved at assembly time and do not appear in output
* **Flexible syntax**

  * Commas are treated as whitespace
    (`add R0,R1,R2` ≡ `add R0 R1 R2`)
* **Immediate handling**

  * Signed 8-bit immediates (`-128 .. 127`)
  * Two’s complement encoding
* **Fail-fast validation**

  * Invalid opcodes, registers, immediates, or unresolved symbols produce clear assembler errors

### Output format

* One instruction per line
* **Zero-padded 8-digit hexadecimal**
* Each line represents a full 32-bit instruction word

Example output:

```
00008803
00000104
02000107
```

## Assembly Grammar (`.dasm`)

This assembler accepts a small, intentionally strict assembly language. Anything outside this grammar is rejected with a clear error. However, the assembler has been built to be easily extensible.

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
- At most **one label per line** is allowed.

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

### Invalid Programs
The assembler rejects programs that contain:
- unknown mnemonics
- invalid registers
- immediates or addresses out of range
- undefined labels
- multiple labels on one line
- malformed instructions

Errors are reported with clear messages indicating the offending line.


---

## Possible Goals

This project intentionally does **not** yet include:

* a virtual machine / executor
* tests or golden outputs
* macros or pseudo-instructions
* inline labels (`label: instr`)
* linking or multiple source files
* debugging symbols

These may be added incrementally later.

---

## Motivation

This project exists to internalize how:

* assembly languages are structured
* labels and symbols are resolved
* instructions are encoded into machine-readable form
* compile-time and runtime responsibilities differ

It is a learning-focused systems project, not a production tool.

---

## Status

🚧 **Work in progress**

The assembler and ISA are functional for the supported instruction set.
Execution (VM) is planned but not yet implemented.

---

## License

MIT License.
