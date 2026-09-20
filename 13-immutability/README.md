# 13. Immutability

See the glossary in [rust_vs_python_ascii_diagrams_cpu.txt](../rust_vs_python_ascii_diagrams_cpu.txt) if a term below is unfamiliar.

```
+-----------------------------------------------------------------+
| PART A - WHAT IT IS (5W+H)                                      |
+-------+---------------------------------------------------------+
| WHAT  | Data that cannot change after it is created. In Rust,   |
|       | variables are unchangeable unless you write 'mut'.      |
+-------+---------------------------------------------------------+
| WHY   | If nothing can change your data behind your back, 'who  |
|       | changed this?' bugs disappear, and threads are safer.   |
+-------+---------------------------------------------------------+
| WHEN  | Sharing data between functions or threads.              |
+-------+---------------------------------------------------------+
| WHERE | Config, shared state, data pipelines.                   |
+-------+---------------------------------------------------------+
| WHO   | Anyone who has debugged a value that changed            |
|       | unexpectedly.                                           |
+-------+---------------------------------------------------------+
| HOW   | Rust: 'let' is locked, 'let mut' can change, and only   |
|       | ONE &mut may exist at a time. Python: everything is     |
|       | changeable by default.                                  |
+-------+---------------------------------------------------------+
```

## PART B — the concept in one picture

```
   Python :  x --> [1, 2, 3]   <-- f(x) can change it
                               <-- g(x) can change it too
                               Who changed it? Search everywhere.

   Rust   :  let x = [1,2,3]   LOCKED by default
             let mut x         may change; only one &mut at a time
```

## PART C — Python vs Rust, step by step

```
             PYTHON                              RUST
+------------------------------+   +------------------------------+
| 1) x = [1, 2, 3]             |   | 1) let x = vec![1, 2, 3];    |
+------------------------------+   |    (immutable by default)    |
               v                   +------------------------------+
+------------------------------+                  v
| 2) Any function that gets    |   +------------------------------+
|    x may change it           |   | 2) x.push(4) is an ERROR     |
+------------------------------+   |    unless: let mut x         |
               v                   +------------------------------+
+------------------------------+                  v
| 3) Caller's list changed     |   +------------------------------+
|    unexpectedly              |   | 3) &mut = only ONE writer    |
+------------------------------+   |    at any moment             |
               v                   +------------------------------+
+------------------------------+                  |
| 4) Classic trap: mutable     |                  |
|    default arguments         |                  |
+------------------------------+                  |
               |                                  |
               v                                  v
  RESULT: surprising side            RESULT: changes are
  effects                            explicit + exclusive
```

(Correctness benefit, not a speed test.)

## PART D — verdict

```
+-----------------------------------------------------------------+
| WHICH IS BETTER?                                                |
+--------+--------------------------------------------------------+
| RUST   | Better when you want the compiler to enforce it.       |
+--------+--------------------------------------------------------+
| PYTHON | Fine with habits: tuples, frozen dataclasses, copying. |
+--------+--------------------------------------------------------+
```

## PART E — why Rust wins here (deep dive)

The rule underneath `let` vs `let mut` is the same **aliasing
invariant** that also powers data-race safety (see
[04-data-race-safety](../04-data-race-safety)): at any point in the
program, for any piece of data, the compiler allows either

```
+-----------------------------------------------------------------+
| THE ALIASING RULE THE BORROW CHECKER ENFORCES                    |
+-----------------------------------------------------------------+
|   many read-only borrows           OR         exactly one        |
|   (&x, &x, &x, ...)                            mutable borrow    |
|                                                 (&mut x)          |
|                                                                   |
|   ... but NEVER both live at the same time.                      |
+-----------------------------------------------------------------+
| let mut x = vec![1, 2, 3];                                       |
| let r1 = &x;        // ok: shared borrow                         |
| let r2 = &x;        // ok: another shared borrow                 |
| x.push(4);          // ERROR: cannot borrow `x` as mutable        |
|                     // because it is also borrowed as immutable   |
| println!("{r1:?}"); // r1/r2 still "alive" here, so the push      |
|                     // above would have invalidated them          |
+-----------------------------------------------------------------+
```

The compiler computes, for every reference, the exact span of code in
which it is used (its "region"), then rejects any overlap between a
`&mut` region and any other region touching the same data. This is
checked once, at compile time, using purely static analysis of the
source — there is no runtime flag or lock involved, so correct code
pays *zero* runtime cost for the guarantee.

Contrast Python: a `list` passed into a function has no marker saying
whether that function intends to read it or mutate it. The only way
to know is to read the function body (or its docs, if any) — the
language gives the compiler/interpreter no information to check
against, so "who changed this?" is always a manual investigation,
never a compiler error.

## Run it

```bash
python python/immutability.py
```

Demonstrates the classic mutable-default-argument trap and an
in-place mutation surprising the caller.

```bash
cd rust
cargo run --release
```

Shows `let` vs `let mut`, and an explicit `&mut` parameter making a
function's intent to mutate visible in its signature.
