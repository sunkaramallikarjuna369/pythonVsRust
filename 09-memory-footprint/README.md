# 9. Memory Footprint

See the glossary in [rust_vs_python_ascii_diagrams_cpu.txt](../rust_vs_python_ascii_diagrams_cpu.txt) if a term below is unfamiliar.

```
+-----------------------------------------------------------------+
| PART A - WHAT IT IS (5W+H)                                      |
+-------+---------------------------------------------------------+
| WHAT  | How much RAM your data takes.                           |
+-------+---------------------------------------------------------+
| WHY   | RAM costs money and limits how much data fits. Smaller  |
|       | data also fits the CPU cache, which is faster.          |
+-------+---------------------------------------------------------+
| WHEN  | Big in-memory datasets, containers with memory limits.  |
+-------+---------------------------------------------------------+
| WHERE | Edge devices, sidecars, in-memory indexes, dense        |
|       | microservices.                                          |
+-------+---------------------------------------------------------+
| WHO   | Anyone paying per GB or hitting out-of-memory errors.   |
+-------+---------------------------------------------------------+
| HOW   | Python: every value is a full object (header +          |
|       | pointers). Rust: plain values packed side by side in    |
|       | one block.                                              |
+-------+---------------------------------------------------------+
```

## PART B — the concept in one picture

```
   Python list of records (pointers to scattered objects):
   [ptr]-->[ header | id | x | y | flag ]-->[int obj][float obj]..
   [ptr]-->[ header | id | x | y | flag ]-->[int obj][float obj]..

   Rust Vec of records (one block, no pointers, 32 bytes each):
   [id x y flag][id x y flag][id x y flag][id x y flag] ...
```

## PART C — Python vs Rust, step by step

```
             PYTHON                              RUST
+------------------------------+   +------------------------------+
| 1) list holds 1M             |   | 1) Vec<Rec> = ONE block      |
|    POINTERS                  |   +------------------------------+
+------------------------------+                  v
               v                   +------------------------------+
+------------------------------+   | 2) Each record = 32 bytes    |
| 2) Each record = an object   |   |    id | x | y | flag         |
|    (16 B header + slots)     |   +------------------------------+
+------------------------------+                  v
               v                   +------------------------------+
+------------------------------+   | 3) Packed side by side,      |
| 3) + separate int and        |   |    no headers, no pointers   |
|    float objects for the     |   +------------------------------+
|    fields                    |                  |
+------------------------------+                  |
               v                                  |
+------------------------------+                  |
| 4) Objects scattered         |                  |
|    around memory             |                  |
+------------------------------+                  |
               |                                  |
               v                                  v
  RESULT: about 161 MB               RESULT: about 31 MB
```

Measured: 161.0 MB vs 30.6 MB = ~5x less RAM.

## PART D — verdict

```
+-----------------------------------------------------------------+
| WHICH IS BETTER?                                                |
+--------+--------------------------------------------------------+
| RUST   | Better for big data in memory (about 5x less RAM in my |
|        | test).                                                 |
+--------+--------------------------------------------------------+
| PYTHON | Fine for small data, or use NumPy/Arrow arrays, which  |
|        | are compact.                                           |
+--------+--------------------------------------------------------+
```

## PART E — why Rust wins here (deep dive)

Rust's advantage comes from **static struct layout**: the compiler
knows every field's exact type and size at compile time, so it can lay
the whole struct out as one fixed-size block with no per-value
bookkeeping.

```
+-----------------------------------------------------------------+
| WHAT ONE `Record` COSTS, BYTE BY BYTE                            |
+-----------------------------------------------------------------+
| struct Record { id: u64, x: f64, y: f64, flag: bool }            |
|                                                                   |
| Rust:  [ id:8B ][ x:8B ][ y:8B ][ flag:1B +7B padding ] = 32B    |
|        computed ONCE by the compiler (size_of::<Record>())       |
|        stored inline, back-to-back, inside the Vec's buffer      |
|                                                                   |
| Python: every field is its OWN heap object with a PyObject       |
|         header (refcount + type pointer, 16B on 64-bit) PLUS     |
|         the list itself only stores an 8B POINTER per record:    |
|                                                                   |
|   list[i] --(8B ptr)--> [16B hdr|slots ptr] --> int obj (28B+)   |
|                                              --> float obj (24B) |
|                                              --> float obj (24B) |
|                                              --> bool (singleton)|
+-----------------------------------------------------------------+
```

Two compounding effects, both fixed by having a compiler that knows
types ahead of time instead of discovering them at run time:

1. **No per-object header.** CPython must tag every value with a type
   pointer and a refcount because *any* name could point to *any*
   type — the interpreter finds out only by reading the header at
   run time. Rust's compiler already proved the type of every field,
   so no header is needed; nothing at run time ever asks "what type
   is this?".
2. **No pointer chasing.** A Python list is an array of pointers to
   objects scattered wherever the allocator happened to put them —
   each field access is a cache miss waiting to happen. A `Vec<Record>`
   is one contiguous allocation; walking it sequentially is exactly
   the access pattern CPU caches and prefetchers are built for, which
   is *also* why the Rust loop in [09-memory-footprint](.) tends to run
   faster, not just use less RAM.

## Run it

```bash
python python/memory_footprint.py
```

```bash
cd rust
cargo run --release
```

Both build 1,000,000 records and report the approximate memory used —
compare the two numbers directly.
