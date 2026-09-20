# 5. Handling Many "Waiting" Tasks At Once

This is about doing other useful work while waiting for something
slow (like a reply from the internet, or a disk), instead of just
sitting there frozen until it's ready.

## Part A — the basics

```
+-----------------------------------------------------------------+
| WHAT IS IT?                                                     |
+-------+---------------------------------------------------------+
| WHAT  | Doing other work while waiting for something slow        |
|       | (network, disk, database) instead of freezing until it   |
|       | finishes.                                                 |
+-------+---------------------------------------------------------+
| WHY   | Waiting wastes time. One slow request shouldn't force     |
|       | thousands of other requests to also sit and wait.         |
+-------+---------------------------------------------------------+
| WHEN  | Handling many connections or requests that spend most of |
|       | their time just waiting.                                  |
+-------+---------------------------------------------------------+
| WHERE | Web servers, systems that connect other services         |
|       | together, programs that scan websites, message systems.  |
+-------+---------------------------------------------------------+
| WHO   | People building backend systems and services that stream |
|       | data.                                                     |
+-------+---------------------------------------------------------+
| HOW   | A task pauses itself at a "wait here" point, and a        |
|       | scheduler runs a different task in the meantime. Python's |
|       | version of this uses a single line of work; Rust's        |
|       | version (a tool called "Tokio") spreads tasks across       |
|       | several lines of work at once.                             |
+-------+---------------------------------------------------------+
```

## Part B — the idea in one picture

```
   Task A : [running]~~~~ waiting on the network ~~~~[running]
   Task B :          [running]~~~~ waiting ~~~~[running]
   Task C :                   [running]~~~~ waiting ~~~~[running]

   While one task is waiting, the CPU works on a different task.
```

## Part C — Python vs Rust, step by step

```
             PYTHON                              RUST
+------------------------------+   +------------------------------+
| 1) One scheduler running on  |   | 1) A scheduler with a pool   |
|    a SINGLE line of work     |   |    of several lines of work  |
+------------------------------+   +------------------------------+
               v                                  v
+------------------------------+   +------------------------------+
| 2) Task reaches a "wait      |   | 2) Task reaches a "wait      |
|    here" point: hands        |   |    here" point: that line of |
|    control back               |   |    work picks up another task |
+------------------------------+   +------------------------------+
               v                                  v
+------------------------------+   +------------------------------+
| 3) The scheduler starts a    |   | 3) Tasks are spread across   |
|    different waiting task    |   |    ALL CPU cores automatically|
+------------------------------+   +------------------------------+
               v                                  |
+------------------------------+                  |
| 4) A heavy calculation in    |                  |
|    any one task freezes      |                  |
|    ALL of them                |                  |
+------------------------------+                  |
               |                                  |
               v                                  v
  RESULT: great for waiting          RESULT: waiting AND heavy
  tasks, only one core used          calculations both spread
  for everything else                 across all cores
```

In a real test: handling 50,000 waiting tasks had a setup cost of
0.561 seconds in Python and only 0.023 seconds in Rust — about 25
times less overhead.

## Part D — the plain verdict

```
+-----------------------------------------------------------------+
| WHICH ONE SHOULD YOU PICK?                                      |
+--------+--------------------------------------------------------+
| RUST   | Better when you need to handle huge numbers of tasks at |
|        | once, or you're mixing heavy calculations with waiting. |
+--------+--------------------------------------------------------+
| PYTHON | Fine for programs that are mostly just waiting, with    |
|        | little actual calculation per request.                  |
+--------+--------------------------------------------------------+
```

## Part E — a deeper look at why Rust handles more tasks so much more cheaply

Both languages use the same basic idea — a task pauses itself at a
"wait here" point and something else runs in the meantime — but how
expensive it is to keep a paused task around is very different.

```
+-----------------------------------------------------------------+
| WHAT A PAUSED RUST TASK ACTUALLY LOOKS LIKE                       |
+-----------------------------------------------------------------+
| A "wait for the network" task, once compiled, turns into a tiny  |
| record that just says which step it's currently on:               |
|                                                                     |
|   step: "just started"                                            |
|   step: "waiting on the network reply"                            |
|   step: "finished"                                                 |
|                                                                     |
| "Pausing" just means: the scheduler stops asking this record       |
| "are you done yet?" for a moment. "Resuming" means: it asks        |
| again. No extra memory is set aside beyond this tiny record —      |
| there's no full snapshot of a running program to keep around.      |
+-----------------------------------------------------------------+
```

Python represents each paused task as a much heavier object: a full
snapshot of a running piece of Python code (its local variables,
exactly which line it's on, and more), managed by a scheduler that is
itself ordinary Python code running on one single line of work.
Resuming a Python task means re-entering the Python reader-program
described in [01-cpu-bound-speed](../01-cpu-bound-speed). Rust's Tokio
tool, on the other hand, is a scheduler written in fast, compiled code
that spreads tasks across **several real lines of work running in
parallel**, and — unlike Python's version — idle lines of work can pick
up extra tasks from busy ones automatically. That's also why a heavy
calculation inside one task doesn't freeze every other task in Rust:
there's usually more than one line of work available to keep going.

That combination — a much smaller "paused task" record, plus more
than one line of work sharing the load — is the real reason 50,000
tasks cost roughly 25 times less overhead in Rust.

## Try it yourself

```bash
python python/async_io.py
```

```bash
cd rust
cargo run --release
```

Both programs start 50,000 tasks that immediately pause and resume,
and report how long handling all of them took.
