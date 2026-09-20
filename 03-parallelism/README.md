# 3. Parallelism

See the glossary in [rust_vs_python_ascii_diagrams_cpu.txt](../rust_vs_python_ascii_diagrams_cpu.txt) if a term below is unfamiliar.

```
+-----------------------------------------------------------------+
| PART A - WHAT IT IS (5W+H)                                      |
+-------+---------------------------------------------------------+
| WHAT  | Doing several pieces of work at the very same moment on |
|       | different CPU cores.                                    |
+-------+---------------------------------------------------------+
| WHY   | Modern CPUs have many cores. A single thread uses only  |
|       | one and leaves the rest idle.                           |
+-------+---------------------------------------------------------+
| WHEN  | Big jobs that can be split into independent pieces.     |
+-------+---------------------------------------------------------+
| WHERE | Batch ETL, image/video processing, big aggregations.    |
+-------+---------------------------------------------------------+
| WHO   | Anyone with a multi-core machine and heavy compute.     |
+-------+---------------------------------------------------------+
| HOW   | Split the data into chunks, give each core a chunk,     |
|       | combine the results. Python's GIL lets only one thread  |
|       | run Python code at a time; Rust has no GIL.             |
+-------+---------------------------------------------------------+
```

## PART B — the concept in one picture

```
   ONE thread : Core 1 [########################]

   FOUR threads on four cores (ideal case):
                Core 1 [######]
                Core 2 [######]
                Core 3 [######]
                Core 4 [######]        ~4x faster
```

## PART C — Python vs Rust, step by step

```
             PYTHON                              RUST
+------------------------------+   +------------------------------+
| 1) Start 4 threads           |   | 1) Start 4 threads           |
+------------------------------+   +------------------------------+
               v                                  v
+------------------------------+   +------------------------------+
| 2) GIL: only ONE thread      |   | 2) No GIL: all threads run   |
|    runs Python code at       |   |    on all CPU cores          |
|    a time                    |   +------------------------------+
+------------------------------+                  v
               v                   +------------------------------+
+------------------------------+   | 3) Rayon: .par_iter()        |
| 3) The other 3 wait          |   |    splits and balances       |
|    (no CPU speed-up)         |   |    the work for you          |
+------------------------------+   +------------------------------+
               v                                  |
+------------------------------+                  |
| 4) Workaround:               |                  |
|    multiprocessing = 4       |                  |
|    processes, copy data,     |                  |
|    more RAM                  |                  |
+------------------------------+                  |
               |                                  |
               v                                  v
  RESULT: threads ~1x,               RESULT: ~N x on N cores,
  processes ~N x minus cost          one-line change
```

Not measurable on a 1-core sandbox: run the parallel programs on your
own multi-core PC to see the real speed-up.

## PART D — verdict

```
+-----------------------------------------------------------------+
| WHICH IS BETTER?                                                |
+--------+--------------------------------------------------------+
| RUST   | Better for CPU work: one line with Rayon, and the      |
|        | compiler checks it is safe.                            |
+--------+--------------------------------------------------------+
| PYTHON | Fine for I/O work, or use multiprocessing / libraries  |
|        | that release the GIL.                                  |
+--------+--------------------------------------------------------+
```

## PART E — why Rust wins here (deep dive)

"No GIL" is the headline, but the reason Rust *can* safely have no GIL
— while C famously needs enormous discipline to avoid data races
without one — is two marker traits the compiler checks for you.

```
+-----------------------------------------------------------------+
| Send AND Sync: THE TWO TRAITS THAT REPLACE THE GIL               |
+-----------------------------------------------------------------+
| Send : "a value of this type can be MOVED to another thread"     |
| Sync : "a reference to this type can be SHARED across threads"   |
|                                                                    |
| thread::spawn(move || { ... })                                   |
|   requires every captured value to be Send                       |
|   -> the compiler checks this at the call site, at compile time  |
|                                                                    |
| Types like Rc<T> (non-atomic refcount) are NOT Send.               |
|   thread::spawn(move || use_rc(rc));  // COMPILE ERROR             |
|   "Rc<T> cannot be sent between threads safely"                    |
|                                                                    |
| Arc<T> (atomic refcount) IS Send + Sync -> compiles fine.          |
+-----------------------------------------------------------------+
```

Rayon's `par_iter()` builds on the same guarantee: it can only split
your iterator across a thread pool because the compiler has already
verified every closure it runs is `Send`. The work-stealing scheduler
then does the scheduling Python's GIL prevents Python threads from
ever benefiting from: idle worker threads "steal" chunks of remaining
work from busy ones, keeping all cores fed without any of your code
managing threads directly.

Python's GIL exists precisely because CPython's reference-counting GC
(see [02-memory-management](../02-memory-management)) is *not*
thread-safe by default — incrementing a plain integer refcount from
two threads at once is itself a data race. Rather than make every
object's refcount atomic (which would slow down single-threaded code),
CPython takes one global lock instead. Rust sidesteps the whole
dilemma: ownership means there's no shared mutable refcount to
protect in the first place.

## Run it

```bash
python python/parallelism.py
```

Compares a single-threaded baseline, 4 GIL-bound threads, and 4
`multiprocessing` workers on the same CPU-bound task.

```bash
cd rust
cargo run --release
```

Compares a single-threaded baseline, 4 plain OS threads, and Rayon's
`par_iter()` — all with no GIL, all on separate cores.
