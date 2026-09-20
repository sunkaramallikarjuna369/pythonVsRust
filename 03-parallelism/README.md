# 3. Doing Several Things At Once On Different CPU Cores

This is about splitting up work so different parts of it run at the
exact same time, on different parts of the processor (most modern
computer chips have several separate "cores" that can each work
independently — like several workers instead of just one).

## Part A — the basics

```
+-----------------------------------------------------------------+
| WHAT IS IT?                                                     |
+-------+---------------------------------------------------------+
| WHAT  | Doing several pieces of work at the exact same moment,   |
|       | on different CPU cores.                                  |
+-------+---------------------------------------------------------+
| WHY   | Modern computer chips have many cores. Using just one of |
|       | them leaves all the others sitting idle, doing nothing.  |
+-------+---------------------------------------------------------+
| WHEN  | Big jobs that can be broken into smaller, independent    |
|       | pieces.                                                   |
+-------+---------------------------------------------------------+
| WHERE | Processing huge batches of data, working on images or    |
|       | video, adding up big piles of numbers.                    |
+-------+---------------------------------------------------------+
| WHO   | Anyone with a multi-core computer and a heavy job to run. |
+-------+---------------------------------------------------------+
| HOW   | Split the data into chunks, give each core its own       |
|       | chunk, then combine the results. In Python, a built-in    |
|       | rule (called the "GIL") only allows ONE line of Python    |
|       | code to run at a time, no matter how many cores you have. |
|       | Rust has no such rule.                                    |
+-------+---------------------------------------------------------+
```

## Part B — the idea in one picture

```
   ONE core doing everything : Core 1 [########################]

   FOUR cores sharing the work (best case):
                Core 1 [######]
                Core 2 [######]
                Core 3 [######]
                Core 4 [######]        about 4 times faster
```

## Part C — Python vs Rust, step by step

```
             PYTHON                              RUST
+------------------------------+   +------------------------------+
| 1) Start 4 separate lines    |   | 1) Start 4 separate lines    |
|    of work ("threads")       |   |    of work ("threads")       |
+------------------------------+   +------------------------------+
               v                                  v
+------------------------------+   +------------------------------+
| 2) Only ONE of them is       |   | 2) No such limit: all 4 can  |
|    allowed to run Python     |   |    run on all 4 CPU cores    |
|    code at any one moment    |   |    at the same time           |
+------------------------------+   +------------------------------+
               v                                  v
+------------------------------+   +------------------------------+
| 3) The other 3 just wait     |   | 3) A helper tool ("Rayon")   |
|    their turn (no real       |   |    splits the work up and    |
|    speed-up)                 |   |    balances it for you        |
+------------------------------+   +------------------------------+
               v                                  |
+------------------------------+                  |
| 4) Workaround: use separate  |                  |
|    full copies of the        |                  |
|    program instead (this     |                  |
|    uses more memory)          |                  |
+------------------------------+                  |
               |                                  |
               v                                  v
  RESULT: threads barely help,       RESULT: close to 4 times
  separate copies help but cost      faster, with a one-line change
  more memory
```

This kind of speed-up depends on your own computer's number of cores,
so it isn't shown as a single measured number here — try the programs
on your own multi-core computer to see it for yourself.

## Part D — the plain verdict

```
+-----------------------------------------------------------------+
| WHICH ONE SHOULD YOU PICK?                                      |
+--------+--------------------------------------------------------+
| RUST   | Better for heavy calculations: one small change gets   |
|        | real speed-up, and the compiler double-checks it's     |
|        | safe.                                                   |
+--------+--------------------------------------------------------+
| PYTHON | Fine for work that spends most of its time waiting     |
|        | (like network calls), or use separate full program     |
|        | copies for heavy calculations.                          |
+--------+--------------------------------------------------------+
```

## Part E — a deeper look at why Rust can safely split work like this

The reason Python needs that "only one line of code at a time" rule,
while Rust doesn't, comes down to what each language's compiler is
willing to check for you before running anything:

```
+-----------------------------------------------------------------+
| TWO CHECKS THE RUST COMPILER RUNS INSTEAD OF A "ONE AT A TIME"   |
| RULE                                                              |
+-----------------------------------------------------------------+
| Check 1: "is it OK to hand this piece of data to another         |
|           thread?"                                                |
| Check 2: "is it OK for two threads to look at this piece of data |
|           at the same time?"                                     |
|                                                                    |
| If you try to hand over a piece of data that ISN'T safe to share, |
| the program simply won't compile — you get an error message      |
| pointing at the exact problem, before the program ever runs.      |
+-----------------------------------------------------------------+
```

A helper tool called "Rayon" builds on top of this: it's only allowed
to split your work across many threads because the compiler has
already double-checked that doing so is safe. Idle cores then borrow
extra pieces of unfinished work from busy ones automatically, so all
your cores stay busy without you having to manage any of that
yourself.

Python's "only one line of code at a time" rule exists because
Python's own background memory helper (the hidden usage-counter system
described in [02-memory-management](../02-memory-management)) isn't
safe to use from two threads at once — updating a simple counter from
two places at the same time can itself go wrong. Rather than making
every single counter update safe on its own (which would slow down
every single-threaded program too), Python instead just locks the
whole thing so only one thread can run code at a time. Rust avoids
this whole problem because there's no shared usage-counter to protect
in the first place.

## Try it yourself

```bash
python python/parallelism.py
```

```bash
cd rust
cargo run --release
```

Both programs compare running the same heavy task on one thread, on
several threads, and (for Rust) using the Rayon helper tool.
