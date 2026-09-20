# 9. How Much Computer Memory The Data Actually Takes Up

This is about how much space your data uses in the computer's memory
(RAM) once it's loaded up — not how fast it runs, but how much room it
needs.

## Part A — the basics

```
+-----------------------------------------------------------------+
| WHAT IS IT?                                                     |
+-------+---------------------------------------------------------+
| WHAT  | How much computer memory your data actually takes up.    |
+-------+---------------------------------------------------------+
| WHY   | Memory costs money and limits how much data can fit at    |
|       | once. Smaller data also fits better into the CPU's own     |
|       | tiny, extra-fast storage, which makes things run faster    |
|       | too.                                                        |
+-------+---------------------------------------------------------+
| WHEN  | Big collections of data held in memory at once, or         |
|       | programs running on machines with limited memory.           |
+-------+---------------------------------------------------------+
| WHERE | Small devices, lightweight background services,            |
|       | in-memory search tools, compact backend services.           |
+-------+---------------------------------------------------------+
| WHO   | Anyone paying for memory by the gigabyte, or running into   |
|       | "out of memory" errors.                                     |
+-------+---------------------------------------------------------+
| HOW   | In Python, every single value is its own full object,      |
|       | with some extra bookkeeping information attached, plus a   |
|       | pointer to it. In Rust, plain values are packed directly    |
|       | next to each other in one solid block, with no extra        |
|       | bookkeeping or pointers in between.                          |
+-------+---------------------------------------------------------+
```

## Part B — the idea in one picture

```
   Python's list of records (a list of POINTERS to scattered objects):
   [pointer]-->[bookkeeping|id|x|y|flag]-->[number object][number object]..
   [pointer]-->[bookkeeping|id|x|y|flag]-->[number object][number object]..

   Rust's list of records (one solid block, no pointers, 32 bytes each):
   [id x y flag][id x y flag][id x y flag][id x y flag] ...
```

## Part C — Python vs Rust, step by step

```
             PYTHON                              RUST
+------------------------------+   +------------------------------+
| 1) The list holds 1 million  |   | 1) One solid block holds ALL |
|    POINTERS to records        |   |    1 million records          |
+------------------------------+   +------------------------------+
               v                                  v
+------------------------------+   +------------------------------+
| 2) Each record is its own     |   | 2) Each record takes exactly |
|    object with bookkeeping    |   |    32 bytes: id, x, y, flag,  |
|    info attached                |   |    laid out right next to     |
+------------------------------+   |    each other                  |
               v                   +------------------------------+
+------------------------------+                  v
| 3) Plus separate number        |   +------------------------------+
|    objects for each of the     |   | 3) No bookkeeping info, no    |
|    fields inside it             |   |    pointers between fields    |
+------------------------------+   +------------------------------+
               v                                  |
+------------------------------+                  |
| 4) All these little objects   |                  |
|    end up scattered around     |                  |
|    in memory                   |                  |
+------------------------------+                  |
               |                                  |
               v                                  v
  RESULT: uses about 161 MB           RESULT: uses about 31 MB
```

In a real test: 1,000,000 records took about 161 MB of memory in
Python and about 31 MB in Rust — about 5 times less.

## Part D — the plain verdict

```
+-----------------------------------------------------------------+
| WHICH ONE SHOULD YOU PICK?                                      |
+--------+--------------------------------------------------------+
| RUST   | Better when holding lots of data in memory at once      |
|        | (about 5 times less memory used in this test).           |
+--------+--------------------------------------------------------+
| PYTHON | Fine for small amounts of data, or use a library that    |
|        | packs numbers tightly, like NumPy or Arrow.               |
+--------+--------------------------------------------------------+
```

## Part E — a deeper look at why Rust's data takes up so much less room

Rust's advantage comes from the compiler knowing, ahead of time,
exactly what type and size every single field is — so it can lay the
whole record out as one fixed-size block with nothing extra attached
to it.

```
+-----------------------------------------------------------------+
| WHAT ONE RECORD COSTS, PIECE BY PIECE                             |
+-----------------------------------------------------------------+
| A record with 4 fields: id (a whole number), x (a decimal          |
| number), y (a decimal number), flag (true/false)                   |
|                                                                     |
| Rust:   [id: 8 bytes][x: 8 bytes][y: 8 bytes][flag + padding: 8]  |
|         = 32 bytes total, worked out once by the compiler,        |
|         stored right next to the previous record, no gaps in       |
|         between except for tiny alignment padding                  |
|                                                                     |
| Python: each field is its OWN separate object with its own         |
|         bookkeeping info (about 16 bytes just for that, on a       |
|         typical computer) attached — and the list itself only       |
|         stores an 8-byte POINTER to each record, not the record     |
|         itself                                                      |
+-----------------------------------------------------------------+
```

Two things stack up here, and both come down to the same root cause:
Python's compiler-equivalent (its reader-program) doesn't know ahead
of time what type anything is, so it has to be ready to handle any
type at any moment.

1. **No extra bookkeeping needed.** Python has to tag every single
   value with information about what type it is and how many places
   are using it, because in Python, any name could turn out to hold
   any type — the reader-program only finds out by checking that
   bookkeeping info while the program runs. Rust's compiler already
   proved what type every field is ahead of time, so none of that
   bookkeeping is needed at all.
2. **No jumping around in memory.** A Python list is really a list of
   pointers to objects scattered wherever they happened to land in
   memory — reading each field means jumping to a different, possibly
   far away, spot in memory each time. Rust's block of records sits
   all together in one place, so reading through them one after
   another is exactly the pattern that makes modern computer chips
   run fastest — which is also part of why the Rust version tends to
   run quicker, not just use less memory.

## Try it yourself

```bash
python python/memory_footprint.py
```

```bash
cd rust
cargo run --release
```

Both programs build 1,000,000 records and report roughly how much
memory was used — compare the two numbers directly.
