# 2. Memory Management

See the glossary in [rust_vs_python_ascii_diagrams_cpu.txt](../rust_vs_python_ascii_diagrams_cpu.txt) if a term below is unfamiliar.

```
+-----------------------------------------------------------------+
| PART A - WHAT IT IS (5W+H)                                      |
+-------+---------------------------------------------------------+
| WHAT  | How a program gets memory for its data and gives it     |
|       | back when finished.                                     |
+-------+---------------------------------------------------------+
| WHY   | Never giving it back = leak (memory grows until a       |
|       | crash). Giving it back too early = crash or corrupted   |
|       | data. Cleaning at bad moments = pauses.                 |
+-------+---------------------------------------------------------+
| WHEN  | Every time you create a list, string or object, which   |
|       | is constantly.                                          |
+-------+---------------------------------------------------------+
| WHERE | Every program. It matters most in long-running services |
|       | and latency-sensitive systems.                          |
+-------+---------------------------------------------------------+
| WHO   | The runtime (Python) or the compiler (Rust) does the    |
|       | work; you feel it as pauses, leaks or speed.            |
+-------+---------------------------------------------------------+
| HOW   | Python counts who uses each object and runs a garbage   |
|       | collector (GC) for cycles. Rust gives each value ONE    |
|       | owner and frees it when the owner leaves scope.         |
+-------+---------------------------------------------------------+
```

## PART B — the concept in one picture

```
   STACK (your variables)          HEAP (the big data)
   +--------------+                +------------------------+
   | name  -------+--------------->| "hello world ..."      |
   +--------------+                +------------------------+

   Who gives the heap box back, and WHEN?
   Python : when nothing points at it any more (+ GC sweeps)
   Rust   : when its single owner leaves scope (known at compile)
```

## PART C — Python vs Rust, step by step

```
             PYTHON                              RUST
+------------------------------+   +------------------------------+
| 1) Create object             |   | 1) A value has ONE owner     |
|    (refcount = 1)            |   +------------------------------+
+------------------------------+                  v
               v                   +------------------------------+
+------------------------------+   | 2) Owner goes out of         |
| 2) Every use changes the     |   |    scope                     |
|    refcount up / down        |   +------------------------------+
+------------------------------+                  v
               v                   +------------------------------+
+------------------------------+   | 3) Compiler already put      |
| 3) Refcount 0 = freed.       |   |    the free() right there    |
|    Cycles need the GC        |   +------------------------------+
+------------------------------+                  |
               v                                  |
+------------------------------+                  |
| 4) GC scans now and then     |                  |
|    = small pauses            |                  |
+------------------------------+                  |
               |                                  |
               v                                  v
  RESULT: automatic but              RESULT: no GC, no
  runtime cost + pauses              pauses, freed on time
```

Measured (3M create+drop of small lists): 0.853 s vs 0.042 s = ~20x

## PART D — verdict

```
+-----------------------------------------------------------------+
| WHICH IS BETTER?                                                |
+--------+--------------------------------------------------------+
| RUST   | Better when steady, predictable latency matters (no GC |
|        | pauses).                                               |
+--------+--------------------------------------------------------+
| PYTHON | Fine for most apps: automatic and easy, pauses rarely  |
|        | matter.                                                |
+--------+--------------------------------------------------------+
```

## PART E — why Rust wins here (deep dive)

Ownership isn't a convention Rust programmers follow — it's a proof
the compiler constructs and checks before it will emit any code.

```
+-----------------------------------------------------------------+
| WHAT THE BORROW CHECKER PROVES, STATICALLY, PER VARIABLE         |
+-----------------------------------------------------------------+
| fn create_and_drop(count: u64) {                                  |
|     for _ in 0..count {                                           |
|         let mut data = vec![0, 1, 2, 3, 4];  // data's region     |
|         data.push(5);                        //   starts here     |
|     } // <- compiler knows: no reference to `data` escapes this   |
|       //    block, so it inserts `drop(data)` RIGHT HERE, at      |
|       //    compile time, as a plain function call in the         |
|       //    generated machine code.                                |
| }                                                                  |
+-----------------------------------------------------------------+
| No runtime object carries a "how many owners do I have?" counter. |
| The answer (always exactly one) was proven before compilation      |
| finished, so there is nothing left to track while the program runs.|
+-----------------------------------------------------------------+
```

Compare what CPython must do for the equivalent Python loop: every
`PyObject` carries a `refcount` field in its header. Creating the list
sets it to 1; appending doesn't change it; `del data` (or the name
going out of scope) decrements it, and *only if it's now zero* does
the allocator reclaim it — a runtime check on every single
create/reassign/delete, plus a separate cyclic garbage collector that
must periodically pause and walk the object graph to catch reference
cycles the counter can't resolve on its own (e.g., two objects
pointing at each other). Rust's ownership graph is acyclic by
construction — the borrow checker rejects the patterns that would
create an uncollectable cycle — so it needs no such sweep at all.

## Run it

```bash
python python/memory_management.py
```

```bash
cd rust
cargo run --release
```

Both create and drop 3,000,000 small collections in a loop and print
the elapsed time.
