# 12. Resource Cleanup

See the glossary in [rust_vs_python_ascii_diagrams_cpu.txt](../rust_vs_python_ascii_diagrams_cpu.txt) if a term below is unfamiliar.

```
+-----------------------------------------------------------------+
| PART A - WHAT IT IS (5W+H)                                      |
+-------+---------------------------------------------------------+
| WHAT  | Giving back what you borrowed from the OS: files,       |
|       | sockets, locks, database connections.                   |
+-------+---------------------------------------------------------+
| WHY   | Unreleased items cause leaks, locked files and 'too     |
|       | many open files' errors.                                |
+-------+---------------------------------------------------------+
| WHEN  | Whenever you open something that must be closed.        |
+-------+---------------------------------------------------------+
| WHERE | File handling, database pools, network code.            |
+-------+---------------------------------------------------------+
| WHO   | Every developer of long-running programs.               |
+-------+---------------------------------------------------------+
| HOW   | Python: a 'with' block closes it (or the GC does,       |
|       | someday). Rust: when the owner leaves scope, Drop runs  |
|       | automatically and closes it (called RAII).              |
+-------+---------------------------------------------------------+
```

## PART B — the concept in one picture

```
   open()  ---->  use it  ---->  close()   <- must happen, or LEAK

   Python : you write 'with' (or hope the GC closes it someday)
   Rust   : the owner leaves scope -> Drop closes it, always
            { let f = File::open("a.txt")?; ... }  <- closed here
```

## PART C — Python vs Rust, step by step

```
             PYTHON                              RUST
+------------------------------+   +------------------------------+
| 1) Open file / lock /        |   | 1) File::open() gives an     |
|    connection                |   |    owner value               |
+------------------------------+   +------------------------------+
               v                                  v
+------------------------------+   +------------------------------+
| 2) Used 'with'? closed at    |   | 2) Owner goes out of         |
|    end of the block          |   |    scope                     |
+------------------------------+   +------------------------------+
               v                                  v
+------------------------------+   +------------------------------+
| 3) Forgot 'with'? closed     |   | 3) Drop runs automatically:  |
|    only when GC frees it     |   |    file closed right there   |
+------------------------------+   +------------------------------+
               v                                  |
+------------------------------+                  |
| 4) Timing unknown =          |                  |
|    possible leak             |                  |
+------------------------------+                  |
               |                                  |
               v                                  v
  RESULT: depends on you             RESULT: always closed,
  remembering                        at a known moment
```

(Correctness benefit, not a speed test.)

## PART D — verdict

```
+-----------------------------------------------------------------+
| WHICH IS BETTER?                                                |
+--------+--------------------------------------------------------+
| RUST   | Better: automatic, always, at a known moment.          |
+--------+--------------------------------------------------------+
| PYTHON | Fine if you always use 'with'.                         |
+--------+--------------------------------------------------------+
```

## PART E — why Rust wins here (deep dive)

RAII (Resource Acquisition Is Initialization) isn't magic — it's the
compiler mechanically inserting cleanup calls based on a **control-flow
analysis** it already has to do for ownership tracking.

```
+-----------------------------------------------------------------+
| HOW THE COMPILER DECIDES WHERE TO INSERT THE CLOSE               |
+-----------------------------------------------------------------+
| fn write_scoped(path: &str) -> io::Result<()> {                  |
|     let mut f = File::create(path)?;   // owner: f               |
|     f.write_all(b"...")?;              // early-return point!    |
|     Ok(())                                                       |
| }   // <- normal exit                                            |
|                                                                   |
| The compiler finds EVERY path out of this function:               |
|   path 1: `?` on File::create fails      -> f never created      |
|   path 2: `?` on write_all fails         -> f WAS created        |
|   path 3: function returns Ok(())        -> f WAS created        |
|                                                                   |
| For every path where `f` was created, it inserts a call to        |
| `Drop::drop(&mut f)` (which closes the file handle) right         |
| before that exit -  this is baked into the compiled machine code, |
| not decided at run time.                                          |
+-----------------------------------------------------------------+
```

This is why it beats "remember to use `with`": the guarantee is
enforced by the compiler examining every exit edge of the function
(normal return, early return, even a panic unwinding through the
frame), not by a human remembering a keyword. In Python, `with` gives
you the same guarantee *if you write it* — but a plain `f = open(...)`
with no `with` compiles and runs fine, and the file only closes
whenever (if ever) the garbage collector gets around to it, or the
process exits.

## Run it

```bash
python python/resource_cleanup.py
```

```bash
cd rust
cargo run --release
```

Both write a temp file and report when it was closed — the Rust
version's `Drop` runs the instant the function returns; nothing to
forget.
