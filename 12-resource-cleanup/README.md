# 12. Making Sure Open Files And Connections Always Get Closed

This is about giving back things you borrowed from the computer's
operating system — open files, network connections, locks, database
connections — once you're done using them.

## Part A — the basics

```
+-----------------------------------------------------------------+
| WHAT IS IT?                                                     |
+-------+---------------------------------------------------------+
| WHAT  | Giving back what you borrowed from the operating system:   |
|       | open files, network connections, locks, database             |
|       | connections.                                                   |
+-------+---------------------------------------------------------+
| WHY   | Not giving these back causes memory to keep filling up,      |
|       | files that stay locked, and "too many things open at once"   |
|       | errors.                                                        |
+-------+---------------------------------------------------------+
| WHEN  | Any time you open something that needs to be closed          |
|       | afterwards.                                                    |
+-------+---------------------------------------------------------+
| WHERE | Working with files, pools of database connections,            |
|       | network code.                                                  |
+-------+---------------------------------------------------------+
| WHO   | Anyone building programs meant to run for a long time.        |
+-------+---------------------------------------------------------+
| HOW   | In Python, wrapping the code in a "with" block closes it      |
|       | automatically at the end (or, if you forget, Python's         |
|       | background helper closes it eventually — someday). In Rust,   |
|       | the moment the one place responsible for it is finished        |
|       | using it, the closing happens automatically. This is           |
|       | usually called "RAII" for short.                                |
+-------+---------------------------------------------------------+
```

## Part B — the idea in one picture

```
   open it  ---->  use it  ---->  close it   <- MUST happen, or it leaks

   Python : you write "with" (or hope the background helper closes
            it for you, eventually)
   Rust   : the moment the responsible place is done, it's closed —
            automatically, no matter how you exit that piece of code
```

## Part C — Python vs Rust, step by step

```
             PYTHON                              RUST
+------------------------------+   +------------------------------+
| 1) Open a file, a lock, or    |   | 1) Opening a file gives you  |
|    a connection                |   |    back the ONE responsible   |
+------------------------------+   |    owner of it                 |
               v                   +------------------------------+
+------------------------------+                  v
| 2) Used "with"? it closes       |   +------------------------------+
|    automatically at the end     |   | 2) That owner finishes being |
+------------------------------+   |    used                         |
               v                   +------------------------------+
+------------------------------+                  v
| 3) Forgot "with"? it only        |   +------------------------------+
|    closes once the background   |   | 3) The closing runs           |
|    helper eventually gets to it |   |    automatically, right at    |
+------------------------------+   |    that exact spot              |
               v                   +------------------------------+
+------------------------------+                  |
| 4) Timing is unknown = a         |                  |
|    possible leak                 |                  |
+------------------------------+                  |
               |                                  |
               v                                  v
  RESULT: depends on you                RESULT: always closed, at
  remembering to do it right              a known, exact moment
```

This is a "does it behave correctly" comparison, not a speed test.

## Part D — the plain verdict

```
+-----------------------------------------------------------------+
| WHICH ONE SHOULD YOU PICK?                                      |
+--------+--------------------------------------------------------+
| RUST   | Better: it happens automatically, always, at a known      |
|        | moment.                                                     |
+--------+--------------------------------------------------------+
| PYTHON | Fine, as long as you always remember to use "with".        |
+--------+--------------------------------------------------------+
```

## Part E — a deeper look at how Rust knows exactly when to close things

This automatic closing isn't magic — the compiler mechanically plants
the "close this" instruction based on the same kind of check it
already does for memory (see
[02-memory-management](../02-memory-management)).

```
+-----------------------------------------------------------------+
| HOW THE COMPILER DECIDES WHERE TO PLANT THE "CLOSE THIS" STEP     |
+-----------------------------------------------------------------+
| A function that opens a file, writes to it, and might fail at      |
| either step:                                                        |
|                                                                       |
|   open the file          // this spot now owns the file             |
|   write to it            // this step could also fail!               |
|   report success                                                     |
|   // <- normal finish                                                |
|                                                                        |
| The compiler works out EVERY single way this function could end:     |
|   way 1: opening the file failed        -> file was never opened     |
|   way 2: writing to it failed            -> file WAS opened           |
|   way 3: it finished successfully         -> file WAS opened           |
|                                                                        |
| For every single ending where the file WAS opened, the compiler       |
| plants a "close this file" step right before that ending — this        |
| is baked into the finished program itself, not decided while the       |
| program happens to be running.                                         |
+-----------------------------------------------------------------+
```

This is why it's more reliable than "remember to use `with`": the
guarantee comes from the compiler examining every single way a piece
of code could end (finishing normally, failing partway through, even
an unexpected crash partway through), not from a person remembering to
type a particular word. In Python, `with` gives you the same guarantee
— but only if you actually write it. Opening a file without `with` is
still perfectly valid Python that runs without complaint — the file
just stays open until the background helper eventually notices, if it
ever gets around to it before the program ends anyway.

## Try it yourself

```bash
python python/resource_cleanup.py
```

```bash
cd rust
cargo run --release
```

Both programs write to a temporary file and report when it was
closed — in Rust, the closing happens automatically the instant the
function finishes, with nothing to remember.
