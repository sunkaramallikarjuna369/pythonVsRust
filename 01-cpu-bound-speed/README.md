# 1. How Fast Each One Runs Heavy Calculations

This is about jobs where the computer's processor (CPU, the chip that
does the actual thinking) is working non-stop: loops, maths, and
number-crunching — not waiting for the internet or a disk.

## Part A — the basics

```
+-----------------------------------------------------------------+
| WHAT IS IT?                                                     |
+-------+---------------------------------------------------------+
| WHAT  | How fast a program runs when the CPU is the busy part:  |
|       | loops, maths, parsing text (not waiting on the network  |
|       | or a hard drive).                                       |
+-------+---------------------------------------------------------+
| WHY   | Slow calculations mean longer jobs, bigger cloud bills, |
|       | and apps that feel sluggish.                            |
+-------+---------------------------------------------------------+
| WHEN  | Any time the program is busy calculating something:     |
|       | going through millions of rows of data, encoding       |
|       | video, running a simulation.                            |
+-------+---------------------------------------------------------+
| WHERE | Turning data into other data, simulations, compressing  |
|       | files, encrypting things, working out statistics.       |
+-------+---------------------------------------------------------+
| WHO   | Anyone whose job takes minutes or hours to run, or gets  |
|       | charged by the second for computer time: people who     |
|       | build data pipelines, backend systems, or games.        |
+-------+---------------------------------------------------------+
| HOW   | Your code is turned into instructions the CPU can       |
|       | follow. Python reads and runs its instructions one at a |
|       | time while the program is running (this reading-as-you- |
|       | go program is called an "interpreter"). Rust turns your |
|       | code into the CPU's own instructions ahead of time,     |
|       | before the program ever runs (this is called            |
|       | "compiling").                                           |
+-------+---------------------------------------------------------+
```

## Part B — the idea in one picture

```
   Work that keeps the CPU busy the whole time (Rust is great here):
   CPU  : [calc][calc][calc][calc][calc][calc][calc]   busy 100%
   Disk : ............ doing nothing ....................

   Work that mostly WAITS (the language matters much less here):
   CPU  : [c].............[c].............[c]..........
   Net  : ..[=====waiting=====]..[=====waiting=====]...
```

## Part C — Python vs Rust, step by step

```
             PYTHON                              RUST
+------------------------------+   +------------------------------+
| 1) Write the .py code        |   | 1) Write the .rs code        |
+------------------------------+   +------------------------------+
               v                                  v
+------------------------------+   +------------------------------+
| 2) Turn it into a simpler    |   | 2) The compiler improves     |
|    set of instructions       |   |    the code ONCE and turns   |
|    (done quickly, every      |   |    it into the CPU's own     |
|    single time you run it)   |   |    instructions              |
+------------------------------+   +------------------------------+
               v                                  v
+------------------------------+   +------------------------------+
| 3) A reader-program looks    |   | 3) The CPU runs those        |
|    at each instruction one   |   |    instructions directly,    |
|    at a time, checks what    |   |    with nothing else in      |
|    kind of value it is, and  |   |    the way                   |
|    then runs it              |   |                               |
+------------------------------+   +------------------------------+
               v                                  |
+------------------------------+                  |
| 4) ...this happens again     |                  |
|    for EVERY step of every   |                  |
|    loop, every single time   |                  |
+------------------------------+                  |
               |                                  |
               v                                  v
  RESULT: slower, with extra          RESULT: faster, nothing
  work done on every step             extra happening while it runs
```

In a real test: finding all prime numbers under 1,000,000 took 2.666
seconds in Python and 0.127 seconds in Rust — Rust was about 21 times
faster.

## Part D — the plain verdict

```
+-----------------------------------------------------------------+
| WHICH ONE SHOULD YOU PICK?                                      |
+--------+--------------------------------------------------------+
| RUST   | Better when your OWN code does the heavy looping (about|
|        | 21 times faster in this test).                         |
+--------+--------------------------------------------------------+
| PYTHON | Fine when the heavy work is already being done by a    |
|        | fast library written in C or Rust (like NumPy or       |
|        | Polars), or when the job is quick anyway.               |
+--------+--------------------------------------------------------+
```

## Part E — a deeper look at why Rust is faster here

Here is what actually happens, step by step, every single time Python
checks whether one number divides evenly into another:

```
+-----------------------------------------------------------------+
| WHAT PYTHON DOES FOR EVERY SINGLE "does n divide by i?" CHECK    |
+-----------------------------------------------------------------+
| 1) look at the next instruction to run                          |
| 2) figure out, right now, what KIND of value n and i are         |
|    (Python doesn't know ahead of time — it has to check)         |
| 3) pick the right piece of internal code to handle that kind     |
|    of value                                                       |
| 4) create a brand new little box in memory to hold the answer    |
| 5) update a hidden "how many things are using this value?"       |
|    counter on the values involved                                 |
| 6) go back to step 1 for the next instruction                     |
+-----------------------------------------------------------------+
| That's 6 steps of bookkeeping just to do one small maths check,   |
| repeated millions and millions of times.                          |
+-----------------------------------------------------------------+

+-----------------------------------------------------------------+
| WHAT RUST DOES, ONCE, BEFORE THE PROGRAM EVER RUNS                |
+-----------------------------------------------------------------+
| The compiler already knows exactly what kind of value n and i    |
| are, so it skips straight to:                                    |
|   - turning "does n divide by i?" into one or two raw CPU steps   |
|   - possibly doing several loop rounds at once for speed          |
|   - keeping n, i, and the answer directly in the CPU's own fast   |
|     working space instead of in memory boxes                      |
+-----------------------------------------------------------------+
| The whole loop becomes a tiny handful of raw CPU steps, with no   |
| checking, no boxing, no hidden counters. That's the ~21x.         |
+-----------------------------------------------------------------+
```

The real reason Python is slower here isn't that it's "worse" — it's
that it has to figure out what kind of thing every value is, again
and again, every single time, because in Python a value could turn
out to be anything. Rust's compiler already worked that out once,
ahead of time, so there's nothing left to figure out while the
program is actually running.

## Try it yourself

```bash
python python/primes.py
```

```bash
cd rust
cargo run --release
```

Both programs count how many prime numbers (numbers only divisible by
1 and themselves) exist below 1,000,000, and print how long it took.
