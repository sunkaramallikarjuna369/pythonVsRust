# 4. Stopping Two Threads From Corrupting Shared Data

This is about making sure that when two separate lines of work
("threads") both look at and change the same piece of data, they
don't step on each other and end up with a wrong answer.

## Part A — the basics

```
+-----------------------------------------------------------------+
| WHAT IS IT?                                                     |
+-------+---------------------------------------------------------+
| WHAT  | Making sure two threads don't read and change the same   |
|       | piece of data at the same moment in a way that corrupts  |
|       | it.                                                       |
+-------+---------------------------------------------------------+
| WHY   | This kind of bug only gives the wrong answer SOMETIMES,   |
|       | which makes it one of the hardest kinds of bug to find.   |
+-------+---------------------------------------------------------+
| WHEN  | Any time two or more threads share a piece of data that  |
|       | at least one of them can change.                          |
+-------+---------------------------------------------------------+
| WHERE | Shared counters, shared caches, shared pools of database  |
|       | connections.                                              |
+-------+---------------------------------------------------------+
| WHO   | Anyone writing code that uses multiple threads.           |
+-------+---------------------------------------------------------+
| HOW   | Use a "lock" (something only one thread can hold at a     |
|       | time) so only one thread changes the value at once.       |
|       | Python leaves it up to you to remember to do this. Rust's |
|       | compiler simply refuses to build code that could have     |
|       | this problem.                                              |
+-------+---------------------------------------------------------+
```

## Part B — the idea in one picture

```
   counter = 5   (after two "add 1" actions, it should end up as 7)

   Thread A : reads 5 ........ adds 1 .... writes 6
   Thread B : ....... reads 5 ........ adds 1 .... writes 6

   Both threads read 5 before either one had written its answer,
   so the final result is 6 — one of the updates got LOST.
   A lock makes Thread B wait until Thread A has fully finished.
```

## Part C — Python vs Rust, step by step

```
             PYTHON                              RUST
+------------------------------+   +------------------------------+
| 1) Two threads both read     |   | 1) Two threads both want to  |
|    counter = 5               |   |    change the same value     |
+------------------------------+   +------------------------------+
               v                                  v
+------------------------------+   +------------------------------+
| 2) Both work out 5 + 1       |   | 2) The compiler checks who   |
+------------------------------+   |    is allowed to touch it     |
               v                   +------------------------------+
+------------------------------+                  v
| 3) Both write 6               |   +------------------------------+
+------------------------------+   | 3) ERROR: the program will   |
               v                   |    not even build, unless    |
+------------------------------+   |    you add a lock             |
| 4) Expected 7, got 6          |   +------------------------------+
|    (one update LOST)          |                  v
+------------------------------+   +------------------------------+
               |                   | 4) With a lock added: one    |
               |                   |    thread at a time, always  |
               |                   |    ends up as 7                |
               |                   +------------------------------+
               |                                  |
               v                                  v
  RESULT: the bug only shows          RESULT: caught before the
  up sometimes, while running         program can even run
```

In a real test: an unlocked counter in Python lost thousands of
updates out of the total; the same counter in Rust, protected by a
lock, always landed on the exact right number.

## Part D — the plain verdict

```
+-----------------------------------------------------------------+
| WHICH ONE SHOULD YOU PICK?                                      |
+--------+--------------------------------------------------------+
| RUST   | Better: this kind of bug simply cannot happen in normal |
|        | Rust code (though threads waiting on each other forever |
|        | is still possible).                                     |
+--------+--------------------------------------------------------+
| PYTHON | Fine for small programs, as long as you always remember |
|        | to use a lock or a queue.                                |
+--------+--------------------------------------------------------+
```

## Part E — a deeper look at why Rust catches this automatically

This is the same underlying rule covered in more detail in
[13-immutability](../13-immutability): the Rust compiler only ever
allows either "many things reading a value" OR "one single thing
changing a value" at the same time — never both together. It applies
this exact same rule across threads, not just within one thread.

```
+-----------------------------------------------------------------+
| WHY A LOCK IS THE ONLY WAY TO CHANGE SHARED DATA ACROSS THREADS  |
+-----------------------------------------------------------------+
| A shared counter, wrapped in a lock, and shared safely across    |
| threads using a small shareable pointer:                          |
|                                                                     |
|   counter += 1;   // this line won't even compile — there's no    |
|                    // way to directly touch the number without    |
|                    // going through the lock first                 |
|                                                                     |
|   ask the lock for permission to change the value                 |
|   change the value                                                 |
|   // permission is automatically given back the moment you're     |
|   // done — this happens on its own, you don't have to remember   |
|   // to do it                                                      |
+-----------------------------------------------------------------+
| There is no path through the code that reaches the number         |
| without asking the lock first — the compiler makes "forgot to     |
| lock it" impossible to even write, not just bad practice.          |
+-----------------------------------------------------------------+
```

That's why the "unsafe" version shown as a comment in the Rust code
for this folder isn't just discouraged — it genuinely refuses to
compile. Two threads both wanting direct, unguarded access to the same
changeable value breaks the "one changer at a time" rule before either
thread even starts running. Python has no such rule built in, so the
identical mistake compiles fine, runs fine most of the time, and only
occasionally produces a wrong number — exactly what you saw in the
Python run above.

## Try it yourself

```bash
python python/data_race.py
```

```bash
cd rust
cargo run --release
```

Both programs have 8 threads add to a shared counter 2,000 times each.
