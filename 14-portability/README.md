# 14. Portability

See the glossary in [rust_vs_python_ascii_diagrams_cpu.txt](../rust_vs_python_ascii_diagrams_cpu.txt) if a term below is unfamiliar.

```
+-----------------------------------------------------------------+
| PART A - WHAT IT IS (5W+H)                                      |
+-------+---------------------------------------------------------+
| WHAT  | Where your program can run: which devices, operating    |
|       | systems and environments.                               |
+-------+---------------------------------------------------------+
| WHY   | More places means more users. Small devices have no     |
|       | room for a heavy interpreter.                           |
+-------+---------------------------------------------------------+
| WHEN  | Targeting browsers, phones, IoT devices, edge servers   |
|       | or different CPUs.                                      |
+-------+---------------------------------------------------------+
| WHERE | WebAssembly in browsers, microcontrollers, edge         |
|       | functions, servers.                                     |
+-------+---------------------------------------------------------+
| WHO   | Product and embedded developers.                        |
+-------+---------------------------------------------------------+
| HOW   | Rust compiles to native code for many targets,          |
|       | including wasm32 and no_std. Python needs an            |
|       | interpreter (Pyodide and MicroPython are cut-down       |
|       | options).                                               |
+-------+---------------------------------------------------------+
```

## PART B — the concept in one picture

```
                        +--> Windows / Linux / macOS
   Rust source ---------+--> ARM chips (phones, Raspberry Pi)
   (one codebase)       +--> WebAssembly (in the browser)
                        +--> tiny embedded chips (no_std)

   Python: an interpreter must exist wherever it runs.
```

## PART C — Python vs Rust, step by step

```
             PYTHON                              RUST
+------------------------------+   +------------------------------+
| 1) Needs a Python            |   | 1) Same Rust source          |
|    interpreter installed     |   +------------------------------+
+------------------------------+                  v
               v                   +------------------------------+
+------------------------------+   | 2) Pick a target: x86, ARM,  |
| 2) Servers and PCs: fine     |   |    wasm32, no_std            |
+------------------------------+   +------------------------------+
               v                                  v
+------------------------------+   +------------------------------+
| 3) Browser: needs a heavy    |   | 3) Runs in browsers (WASM),  |
|    runtime (e.g. Pyodide)    |   |    edge, embedded, servers   |
+------------------------------+   +------------------------------+
               v                                  |
+------------------------------+                  |
| 4) Tiny chips: only a        |                  |
|    cut-down MicroPython      |                  |
+------------------------------+                  |
               |                                  |
               v                                  v
  RESULT: limited reach              RESULT: runs where
                                     Python can't
```

(Reach benefit, not a speed test.)

## PART D — verdict

```
+-----------------------------------------------------------------+
| WHICH IS BETTER?                                                |
+--------+--------------------------------------------------------+
| RUST   | Better when you need browser, edge or embedded reach.  |
+--------+--------------------------------------------------------+
| PYTHON | Fine on servers and PCs.                               |
+--------+--------------------------------------------------------+
```

## PART E — why Rust wins here (deep dive)

The reach comes from what a "target" actually needs to run compiled
output — and how little Rust's runtime requires.

```
+-----------------------------------------------------------------+
| WHAT EACH TARGET NEEDS TO RUN THE PROGRAM                        |
+-----------------------------------------------------------------+
| x86_64-linux    : rustc -> LLVM backend "x86-64" -> native exe   |
|                    needs: an OS (for syscalls). That's it.       |
|                                                                   |
| wasm32-unknown  : rustc -> LLVM backend "wasm32" -> .wasm module |
|                    needs: any WASM host (browser, wasmtime).     |
|                    no OS assumptions baked in - std is opt-out.  |
|                                                                   |
| thumbv7em (MCU) : rustc -> LLVM backend "ARM Cortex-M" -> .elf   |
|                    needs: nothing - #[no_std] means the binary   |
|                    brings its own tiny "core" library, no OS,    |
|                    no heap allocator required unless you add one |
+-----------------------------------------------------------------+
| All three come from the SAME source file and the SAME frontend   |
| (rustc's type/borrow checking runs once); only LLVM's CODE-      |
| GENERATION backend changes per target.                           |
+-----------------------------------------------------------------+
```

Python's portability problem is structural, not a tooling gap: running
a `.py` file means running the CPython *interpreter* (megabytes of C
code implementing the object model, GC, bytecode dispatch, and the
standard library) on that target first. A browser has no way to run
arbitrary native C, so Pyodide instead compiles the entire CPython
interpreter itself to WASM — you ship an interpreter plus your script,
not just your script. A microcontroller with kilobytes of RAM has no
room for that interpreter at all, so MicroPython exists as a
from-scratch, cut-down reimplementation with fewer features.

Rust never ships an interpreter because there isn't one: `rustc`
already did all the type checking, memory-safety proof, and
optimization at build time, on your dev machine. What ships to the
tiny device is just the machine code left over — no runtime needed to
make sense of it beyond what the CPU itself provides.

## Run it

```bash
python python/note.py
```

Prints what your current machine needs to run Python at all, and what
browsers/microcontrollers would additionally require.

```bash
cd rust
cargo run --release
```

Runs the portable `add()` function natively. To see it target the
browser instead:

```bash
rustup target add wasm32-unknown-unknown
cargo build --release --target wasm32-unknown-unknown
```
