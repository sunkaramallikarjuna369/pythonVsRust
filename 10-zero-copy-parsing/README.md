# 10. Zero-Copy Parsing

See the glossary in [rust_vs_python_ascii_diagrams_cpu.txt](../rust_vs_python_ascii_diagrams_cpu.txt) if a term below is unfamiliar.

```
+-----------------------------------------------------------------+
| PART A - WHAT IT IS (5W+H)                                      |
+-------+---------------------------------------------------------+
| WHAT  | Reading data by pointing at the original bytes instead  |
|       | of making a new copy of each piece.                     |
+-------+---------------------------------------------------------+
| WHY   | Copying costs time and memory, multiplied by millions   |
|       | of records.                                             |
+-------+---------------------------------------------------------+
| WHEN  | Parsing big files or streams: logs, CSV, JSON, network  |
|       | messages.                                               |
+-------+---------------------------------------------------------+
| WHERE | Log processors, ingestion pipelines, protocol parsers.  |
+-------+---------------------------------------------------------+
| WHO   | Data engineers ingesting large volumes.                 |
+-------+---------------------------------------------------------+
| HOW   | Rust's &str is a slice: a start position + a length     |
|       | pointing INTO the original buffer. Python's split()     |
|       | builds brand-new string objects.                        |
+-------+---------------------------------------------------------+
```

## PART B — the concept in one picture

```
   buffer :  1,ERROR,user9,45
             ^ ^^^^^ ^^^^^ ^^
   Rust   :  slices = (start, length) INTO the buffer
             "ERROR" = (2, 5)   -> no new memory used
   Python :  "1"  "ERROR"  "user9"  "45"  -> 4 NEW string objects
```

## PART C — Python vs Rust, step by step

```
             PYTHON                              RUST
+------------------------------+   +------------------------------+
| 1) Text buffer in memory     |   | 1) Text buffer in memory     |
+------------------------------+   +------------------------------+
               v                                  v
+------------------------------+   +------------------------------+
| 2) line.split(',') builds    |   | 2) split(',') gives &str =   |
|    NEW string objects        |   |    pointer + length INTO     |
+------------------------------+   |    the same buffer           |
               v                   +------------------------------+
+------------------------------+                  v
| 3) int(p[3]) converts        |   +------------------------------+
|    another copy              |   | 3) Parse in place: no        |
+------------------------------+   |    copy, no new strings      |
               v                   +------------------------------+
+------------------------------+                  |
| 4) Many allocations for      |                  |
|    millions of lines         |                  |
+------------------------------+                  |
               |                                  |
               v                                  v
  RESULT: more allocation,           RESULT: far fewer
  more time                          allocations
```

Measured (2M CSV lines): 0.358 s vs 0.097 s = ~4x.

## PART D — verdict

```
+-----------------------------------------------------------------+
| WHICH IS BETTER?                                                |
+--------+--------------------------------------------------------+
| RUST   | Better for very large streams (about 4x in my test).   |
+--------+--------------------------------------------------------+
| PYTHON | Fine for moderate files (split() itself runs as fast C |
|        | code), or use pandas/Polars.                           |
+--------+--------------------------------------------------------+
```

## PART E — why Rust wins here (deep dive)

The interesting part isn't the speed — it's *why slicing without
copying is even safe*. In C, returning a pointer into a buffer that
might later be freed is a classic dangling-pointer bug. Rust makes the
same trick safe using **lifetimes**, a piece of the borrow checker.

```
+-----------------------------------------------------------------+
| WHAT A LIFETIME ACTUALLY BUYS YOU                                |
+-----------------------------------------------------------------+
| fn parse_line<'a>(line: &'a str) -> Vec<&'a str> {               |
|     line.split(',').collect()                                   |
| }                                                                 |
|                                                                   |
| The signature says: "every &str I hand back borrows from, and    |
| cannot outlive, the `line` you gave me."                         |
|                                                                   |
|   let parts;                                                     |
|   {                                                               |
|       let buffer = String::from("1,ERROR,user9,45");             |
|       parts = parse_line(&buffer);                               |
|   } // buffer freed here                                         |
|   println!("{:?}", parts); // COMPILE ERROR: `buffer` does not   |
|                             // live long enough                  |
+-----------------------------------------------------------------+
```

The compiler tracks, for every reference, the region of code in which
it is valid, and rejects any use of that reference outside that
region. That is what turns "pointer + length into someone else's
memory" from a footgun into a checked, zero-cost operation — the
`&str` slice is literally just `(pointer, length)` at runtime, exactly
like the raw pointer trick, but the compiler proves beforehand that it
can never dangle.

Python's `line.split(',')` can't return slices of `line` at all
because Python strings are immutable *objects*, not raw buffers a
lightweight view can point into from user code — so a fresh string
object is the only option, every time.

## Run it

```bash
python python/zero_copy_parsing.py
```

```bash
cd rust
cargo run --release
```

Both parse 2,000,000 CSV-style lines and sum one integer column.
