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

---

## Example

Input (`example.dasm`):

```
loop:
    ldi R0 -120
    prr R0
    beq R0 loop
    hlt
```

Assembly resolves `loop` to instruction address `0` and emits machine code with that address encoded directly.

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
