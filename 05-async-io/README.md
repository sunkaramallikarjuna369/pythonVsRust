# 5. Async I/O

See the glossary in [rust_vs_python_ascii_diagrams_cpu.txt](../rust_vs_python_ascii_diagrams_cpu.txt) if a term below is unfamiliar.

```
+-----------------------------------------------------------------+
| PART A - WHAT IT IS (5W+H)                                      |
+-------+---------------------------------------------------------+
| WHAT  | Doing other work while waiting for slow things          |
|       | (network, disk, database) instead of freezing.          |
+-------+---------------------------------------------------------+
| WHY   | Waiting wastes time. One slow request should not block  |
|       | thousands of others.                                    |
+-------+---------------------------------------------------------+
| WHEN  | Many connections or requests that spend most of their   |
|       | time waiting.                                           |
+-------+---------------------------------------------------------+
| WHERE | Web servers, API gateways, crawlers, message consumers. |
+-------+---------------------------------------------------------+
| WHO   | Backend and data-streaming developers.                  |
+-------+---------------------------------------------------------+
| HOW   | A task pauses at 'await' and a scheduler runs another   |
|       | task. Python's asyncio uses one thread; Rust's Tokio    |
|       | uses many threads.                                      |
+-------+---------------------------------------------------------+
```

## PART B — the concept in one picture

```
   Task A : [run]~~~~ waiting for network ~~~~[run]
   Task B :       [run]~~~~ waiting ~~~~[run]
   Task C :             [run]~~~~ waiting ~~~~[run]

   While one task waits, the CPU works on another task.
```

## PART C — Python vs Rust, step by step

```
             PYTHON                              RUST
+------------------------------+   +------------------------------+
| 1) asyncio: one event        |   | 1) Tokio runtime with        |
|    loop on ONE thread        |   |    a pool of worker threads  |
+------------------------------+   +------------------------------+
               v                                  v
+------------------------------+   +------------------------------+
| 2) Task hits await:          |   | 2) Task hits .await:         |
|    hands control back        |   |    thread runs another task  |
+------------------------------+   +------------------------------+
               v                                  v
+------------------------------+   +------------------------------+
| 3) Loop starts another       |   | 3) Tasks spread over ALL     |
|    waiting task              |   |    cores (work stealing)     |
+------------------------------+   +------------------------------+
               v                                  |
+------------------------------+                  |
| 4) CPU-heavy code in any     |                  |
|    task BLOCKS them all      |                  |
+------------------------------+                  |
               |                                  |
               v                                  v
  RESULT: fine for I/O,              RESULT: I/O + CPU work
  one core for the rest              scale across cores
```

Measured (50,000 tasks): overhead 0.561 s vs 0.023 s = ~25x less.

## PART D — verdict

```
+-----------------------------------------------------------------+
| WHICH IS BETTER?                                                |
+--------+--------------------------------------------------------+
| RUST   | Better when you have huge concurrency, or CPU work     |
|        | mixed in with I/O.                                     |
+--------+--------------------------------------------------------+
| PYTHON | Fine for I/O-heavy programs with little CPU work per   |
|        | request.                                               |
+--------+--------------------------------------------------------+
```

## PART E — why Rust wins here (deep dive)

Both languages use the same core idea — a task suspends at an await
point and something else runs meanwhile — but *what a suspended task
costs to keep around* differs by an order of magnitude.

```
+-----------------------------------------------------------------+
| WHAT AN `async fn` ACTUALLY COMPILES TO IN RUST                  |
+-----------------------------------------------------------------+
| async fn fake_request(id: usize) -> usize {                       |
|     tokio::time::sleep(Duration::from_secs(0)).await;             |
|     id                                                             |
| }                                                                   |
|                                                                     |
| The compiler turns this into a hand-written-quality STATE MACHINE  |
| (an enum) with one variant per suspend point:                      |
|                                                                     |
|   enum FakeRequestState {                                          |
|       Start(usize),                                                |
|       WaitingOnSleep(usize, tokio::time::Sleep),                   |
|       Done,                                                        |
|   }                                                                 |
|                                                                     |
| "Awaiting" is just returning Poll::Pending from this state          |
| machine's poll() method; resuming is calling poll() again. No       |
| stack, no frame object, no heap allocation beyond the enum itself.  |
+-----------------------------------------------------------------+
```

Python's `asyncio` represents each suspended coroutine as a full
Python-level object: a `coroutine` wrapping a real interpreter frame
(locals, the bytecode instruction pointer, exception state), scheduled
by a single-threaded event loop that is itself just Python code making
`select`/`epoll` calls. Every resume re-enters the bytecode
interpreter. Tokio's tasks are plain structs polled by a scheduler
written in Rust, running across a **work-stealing pool of OS threads**
— so unlike `asyncio`, a CPU-heavy task doesn't block every other task
on the same thread, because there usually isn't just one thread.

That's the concrete reason 50,000 Tokio tasks cost roughly 25x less
overhead than 50,000 asyncio tasks: each one is a small stack-allocated
enum polled directly, not a heap-allocated interpreter frame walked by
another layer of Python.

## Run it

```bash
python python/async_io.py
```

```bash
cd rust
cargo run --release
```

Both spawn 50,000 tasks that immediately yield (`asyncio.sleep(0)` /
`tokio::time::sleep(0)`) and report how long scheduling all of them
took.
