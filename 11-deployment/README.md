# 11. Deployment

See the glossary in [rust_vs_python_ascii_diagrams_cpu.txt](../rust_vs_python_ascii_diagrams_cpu.txt) if a term below is unfamiliar.

```
+-----------------------------------------------------------------+
| PART A - WHAT IT IS (5W+H)                                      |
+-------+---------------------------------------------------------+
| WHAT  | Getting your program from your laptop to run somewhere  |
|       | else: a server, container or customer PC.               |
+-------+---------------------------------------------------------+
| WHY   | More moving parts means more things that can break,     |
|       | bigger images and slower start-up.                      |
+-------+---------------------------------------------------------+
| WHEN  | Every release, and especially for serverless functions  |
|       | that start often.                                       |
+-------+---------------------------------------------------------+
| WHERE | Docker, Cloud Run / Lambda, tools you hand to other     |
|       | people.                                                 |
+-------+---------------------------------------------------------+
| WHO   | DevOps and anyone shipping software.                    |
+-------+---------------------------------------------------------+
| HOW   | Python: ship an interpreter + virtualenv + libraries +  |
|       | your code. Rust: build one binary file and copy it.     |
+-------+---------------------------------------------------------+
```

## PART B — the concept in one picture

```
   Python package to ship:            Rust package to ship:
   +---------------------------+      +----------------+
   | Python interpreter        |      |                |
   | virtualenv                |      |   ONE binary   |
   | libraries (pip)           |      |   (.exe)       |
   | your .py code             |      |                |
   +---------------------------+      +----------------+
```

## PART C — Python vs Rust, step by step

```
             PYTHON                              RUST
+------------------------------+   +------------------------------+
| 1) Install the right         |   | 1) cargo build --release     |
|    Python version            |   +------------------------------+
+------------------------------+                  v
               v                   +------------------------------+
+------------------------------+   | 2) Get ONE binary file       |
| 2) Create a virtualenv       |   |    (dependencies inside)     |
+------------------------------+   +------------------------------+
               v                                  v
+------------------------------+   +------------------------------+
| 3) pip install every         |   | 3) Copy it, run it           |
|    dependency                |   |    (~1 ms start)             |
+------------------------------+   +------------------------------+
               v                                  |
+------------------------------+                  |
| 4) Ship code + venv, start   |                  |
|    interpreter (~9 ms)       |                  |
+------------------------------+                  |
               |                                  |
               v                                  v
  RESULT: many moving                RESULT: one file, tiny
  parts                              container image
```

Measured start-up: 9.34 ms vs 0.91 ms; hello binary ~338 KB.

## PART D — verdict

```
+-----------------------------------------------------------------+
| WHICH IS BETTER?                                                |
+--------+--------------------------------------------------------+
| RUST   | Better for tiny images, fast cold starts and tools you |
|        | give to others.                                        |
+--------+--------------------------------------------------------+
| PYTHON | Fine when Docker/CI already manage your environment.   |
+--------+--------------------------------------------------------+
```

## PART E — why Rust wins here (deep dive)

The gap traces back to *when* work happens: link time vs. every
process start.

```
+-----------------------------------------------------------------+
| WHAT HAPPENS THE INSTANT YOU TYPE `./program` OR `python app.py` |
+-----------------------------------------------------------------+
| Rust binary:                                                     |
|   OS loader maps the ELF/PE file's pages into memory             |
|   -> jumps straight to `main` (dependencies already linked       |
|      in at BUILD time by rustc/LLVM, mostly statically)          |
|   -> ~1 ms                                                       |
|                                                                   |
| Python script:                                                   |
|   OS loader starts the `python` executable                       |
|   -> interpreter initializes: builds the module import system,   |
|      compiles/loads the standard library's own .py/.pyc files,   |
|      sets up the GC, sets up type objects for every builtin      |
|   -> resolves and imports your dependencies from disk (pip site- |
|      packages), each one running ITS OWN top-level Python code   |
|   -> only THEN starts running `app.py`                           |
|   -> ~9 ms, and grows with every import you add                  |
+-----------------------------------------------------------------+
```

Rust pays its "linking" cost once, at `cargo build --release` time,
producing a binary that already knows exactly which machine code to
jump to for every function call. Python defers almost all of that
resolution to run time — it re-discovers what every imported module
contains on every single process start, because nothing is compiled
ahead of time to a fixed address. That is also why a Rust binary can
be copied to another machine and just run: there is no "was the right
interpreter version installed with the right packages?" step left to
fail.

## Run it

```bash
python python/hello.py
```

```bash
cd rust
cargo build --release
./target/release/hello
```

Time either with your shell's `time` command to compare cold-start
latency.
