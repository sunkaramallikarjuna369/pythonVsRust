# 4. Data-Race Safety

See the glossary in [rust_vs_python_ascii_diagrams_cpu.txt](../rust_vs_python_ascii_diagrams_cpu.txt) if a term below is unfamiliar.

```
+-----------------------------------------------------------------+
| PART A - WHAT IT IS (5W+H)                                      |
+-------+---------------------------------------------------------+
| WHAT  | Making sure two threads do not read and change the same |
|       | data at the same time in a way that corrupts it.        |
+-------+---------------------------------------------------------+
| WHY   | Races give wrong answers only SOMETIMES, which makes    |
|       | them some of the hardest bugs to find.                  |
+-------+---------------------------------------------------------+
| WHEN  | Any time threads share data that at least one of them   |
|       | can change.                                             |
+-------+---------------------------------------------------------+
| WHERE | Shared counters, caches, connection pools.              |
+-------+---------------------------------------------------------+
| WHO   | Anyone writing multi-threaded code.                     |
+-------+---------------------------------------------------------+
| HOW   | Use locks or atomics so only one thread changes the     |
|       | value at a time. Python: you must remember to. Rust:    |
|       | the compiler refuses code that could race.              |
+-------+---------------------------------------------------------+
```

## PART B — the concept in one picture

```
   counter = 5   (after two increments it should be 7)

   Thread A : read 5 ........ add .... write 6
   Thread B : ....... read 5 ........ add .... write 6

   Both read 5 before either wrote -> final = 6, one update LOST.
   A lock (Mutex) makes B wait until A has finished writing.
```

## PART C — Python vs Rust, step by step

```
             PYTHON                              RUST
+------------------------------+   +------------------------------+
| 1) 2 threads both read       |   | 1) 2 threads want to         |
|    counter = 5               |   |    change the same value     |
+------------------------------+   +------------------------------+
               v                                  v
+------------------------------+   +------------------------------+
| 2) Both compute 5 + 1        |   | 2) Compiler checks who       |
+------------------------------+   |    owns / shares it          |
               v                   +------------------------------+
+------------------------------+                  v
| 3) Both write 6              |   +------------------------------+
+------------------------------+   | 3) ERROR: will not build     |
               v                   |    unless you use Mutex      |
+------------------------------+   |    or an atomic              |
| 4) Expected 7, got 6         |   +------------------------------+
|    (update LOST)             |                  v
+------------------------------+   +------------------------------+
               |                   | 4) With Mutex: one at a      |
               |                   |    time, always 7            |
               |                   +------------------------------+
               |                                  |
               v                                  v
  RESULT: bug shows at               RESULT: bug caught at
  RUNTIME, only sometimes            COMPILE time
```

Measured: Python lost updates under an unlocked counter; Rust with a
`Mutex` always lands on the exact expected total.

## PART D — verdict

```
+-----------------------------------------------------------------+
| WHICH IS BETTER?                                                |
+--------+--------------------------------------------------------+
| RUST   | Better: data races cannot happen in safe Rust          |
|        | (deadlocks still can).                                 |
+--------+--------------------------------------------------------+
| PYTHON | Fine for small programs if you always use a Lock or a  |
|        | queue.                                                 |
+--------+--------------------------------------------------------+
```

## PART E — why Rust wins here (deep dive)

This is the same aliasing rule from
[13-immutability](../13-immutability), extended across threads: the
borrow checker's "one writer XOR many readers" invariant doesn't
distinguish between two closures in one thread and two closures on two
different threads — the rule is identical either way.

```
+-----------------------------------------------------------------+
| WHY `Mutex<T>` IS THE *ONLY* WAY TO GET A MUTABLE REFERENCE       |
| TO SHARED DATA ACROSS THREADS                                     |
+-----------------------------------------------------------------+
| let counter = Arc::new(Mutex::new(0u64));                         |
|                                                                     |
| Arc<Mutex<u64>> shares OWNERSHIP of the Mutex across threads       |
| (Arc = atomic refcount, safe to share - see PART E of              |
| 03-parallelism). But the u64 INSIDE is never directly reachable:   |
|                                                                     |
|   counter += 1;              // does not even compile:            |
|                               // Arc<Mutex<u64>> has no `+=`        |
|                                                                     |
|   let mut value = counter.lock().unwrap();  // returns a           |
|                                              // MutexGuard<u64>     |
|   *value += 1;               // only the guard can deref to &mut   |
|   // guard dropped here -> lock released, exactly once, by Drop    |
+-----------------------------------------------------------------+
| The type system makes "forgot to lock" a type error, not a         |
| runtime possibility: there is no code path that reaches the u64    |
| without holding the guard that the Mutex handed out.               |
+-----------------------------------------------------------------+
```

This is why the comment in [rust/src/main.rs](rust/src/main.rs)
showing the naive `counter += 1` across threads isn't just "bad
practice" — it is a compile error (`E0499`/`E0373`), because a plain
shared variable captured by two `thread::spawn` closures would give
two threads a `&mut` to the same memory at the same time, which
violates the aliasing rule before either thread even starts running.
Python has no such rule to check against, so the identical bug
compiles, runs, and only shows up as a wrong number sometimes — as
seen in the Python run above.

## Run it

```bash
python python/data_race.py
```

Runs 8 threads incrementing a shared counter with no lock (lost
updates every time — a deliberate `time.sleep(0)` widens the race
window so it doesn't depend on scheduling luck) and then again with a
`threading.Lock` (always correct).

```bash
cd rust
cargo run --release
```

Same 8-thread counter, protected by `Arc<Mutex<u64>>` — the unsafe,
unprotected version is left as a comment because it genuinely will not
compile in Rust.
