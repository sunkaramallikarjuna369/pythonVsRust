# 1. CPU-Bound Speed

See the glossary in [rust_vs_python_ascii_diagrams_cpu.txt](../rust_vs_python_ascii_diagrams_cpu.txt) if a term below is unfamiliar.

```
+-----------------------------------------------------------------+
| PART A - WHAT IT IS (5W+H)                                      |
+-------+---------------------------------------------------------+
| WHAT  | How fast a program runs when the CPU itself is the busy |
|       | part: loops, maths, parsing (not waiting for network or |
|       | disk).                                                  |
+-------+---------------------------------------------------------+
| WHY   | Slow compute = longer jobs, bigger cloud bills, laggy   |
|       | apps.                                                   |
+-------+---------------------------------------------------------+
| WHEN  | Whenever the program is busy calculating: transforming  |
|       | millions of rows, encoding, simulations.                |
+-------+---------------------------------------------------------+
| WHERE | Data transforms, simulations, compression, crypto,      |
|       | feature calculation.                                    |
+-------+---------------------------------------------------------+
| WHO   | Anyone whose job runs for minutes/hours or is billed    |
|       | per CPU-second: data engineers, backend and game        |
|       | developers.                                             |
+-------+---------------------------------------------------------+
| HOW   | Your code becomes CPU instructions. Python reads and    |
|       | runs them one by one at run time (interpreter). Rust    |
|       | converts them ahead of time into machine code (LLVM).   |
+-------+---------------------------------------------------------+
```

## PART B — the concept in one picture

```
   CPU-bound (the CPU never rests - this is where Rust shines):
   CPU  : [calc][calc][calc][calc][calc][calc][calc]   busy 100%
   Disk : ............ idle ............................

   I/O-bound (the language matters much less):
   CPU  : [c].............[c].............[c]..........
   Net  : ..[=====waiting=====]..[=====waiting=====]...
```

## PART C — Python vs Rust, step by step

```
             PYTHON                              RUST
+------------------------------+   +------------------------------+
| 1) Write .py code            |   | 1) Write .rs code            |
+------------------------------+   +------------------------------+
               v                                  v
+------------------------------+   +------------------------------+
| 2) Compile to bytecode       |   | 2) Compiler (LLVM) opti-     |
|    (quick, every run)        |   |    mizes ONCE, emits         |
+------------------------------+   |    machine code              |
               v                   +------------------------------+
+------------------------------+                  v
| 3) Interpreter loop reads    |   +------------------------------+
|    each instruction,         |   | 3) CPU runs the machine      |
|    checks types, runs it     |   |    code directly             |
+------------------------------+   +------------------------------+
               v                                  |
+------------------------------+                  |
| 4) ...repeated for EVERY     |                  |
|    step of every loop        |                  |
+------------------------------+                  |
               |                                  |
               v                                  v
  RESULT: slower, extra              RESULT: faster, no
  work on every step                 middle layer at runtime
```

Measured: 2.666 s vs 0.127 s (primes < 1M) = ~21x

## PART D — verdict

```
+-----------------------------------------------------------------+
| WHICH IS BETTER?                                                |
+--------+--------------------------------------------------------+
| RUST   | Better when the heavy loops are in YOUR code (about    |
|        | 21x faster in my test).                                |
+--------+--------------------------------------------------------+
| PYTHON | Fine when the heavy work already runs inside C/Rust    |
|        | libraries (NumPy, Polars) or the job is short.         |
+--------+--------------------------------------------------------+
```

## PART E — why Rust wins here (deep dive)

"Compiled vs interpreted" undersells it. Here's what actually happens
on every single loop iteration of `is_prime`:

```
+-----------------------------------------------------------------+
| PYTHON: what the interpreter does for EVERY `n % i == 0`         |
+-----------------------------------------------------------------+
| 1) fetch the next bytecode instruction (BINARY_MODULO)           |
| 2) look up the runtime TYPE of n and i (could be int, could be   |
|    anything - Python doesn't know until it checks)                |
| 3) dispatch to the correct C function for that type combination  |
| 4) allocate a NEW PyObject to box the result                      |
| 5) bump/decrement reference counts on objects touched             |
| 6) jump back to step 1 for the next instruction                   |
+-----------------------------------------------------------------+
| That is ~6 steps of bookkeeping around ONE modulo operation,      |
| repeated for every candidate i, for every candidate n.            |
+-----------------------------------------------------------------+

+-----------------------------------------------------------------+
| RUST: what the compiler does ONCE, before the program ever runs  |
+-----------------------------------------------------------------+
| rustc -> MIR -> LLVM IR -> LLVM's optimizer:                     |
|   - types are fixed at compile time: no runtime type checks       |
|   - `n % i == 0` compiles straight to a CPU DIV+CMP instruction   |
|   - the whole `while` loop gets inlined and often unrolled         |
|   - no boxing: n, i, and the result live in CPU registers          |
+-----------------------------------------------------------------+
| The loop body becomes a handful of native instructions with no    |
| dispatch, no boxing, and no refcounting - that's the ~21x.        |
+-----------------------------------------------------------------+
```

The deeper point: Python's cost isn't the language's syntax, it's that
*every operation must re-discover what it's operating on* because
values can be any type at any time. Rust's compiler already proved
what type everything is before generating a single instruction, so
that discovery step is eliminated entirely rather than made faster.

## Run it

```bash
python python/primes.py
```

```bash
cd rust
cargo run --release
```

Both count primes below 1,000,000 with plain trial division and print
the elapsed time — compare the two numbers yourself.
