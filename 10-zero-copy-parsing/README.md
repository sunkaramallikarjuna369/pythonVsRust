# 10. Reading Data Without Making Extra Copies Of It

This is about reading through a big chunk of text (like a data file)
by just pointing at the pieces you need, instead of copying each piece
out into a brand new bit of memory.

## Part A — the basics

```
+-----------------------------------------------------------------+
| WHAT IS IT?                                                     |
+-------+---------------------------------------------------------+
| WHAT  | Reading data by pointing directly at the original text,   |
|       | instead of making a brand new copy of every single piece. |
+-------+---------------------------------------------------------+
| WHY   | Copying costs time and memory, and that cost multiplies    |
|       | when you're reading millions of records.                   |
+-------+---------------------------------------------------------+
| WHEN  | Reading through big files or streams: logs, spreadsheets   |
|       | of data, structured messages, network messages.             |
+-------+---------------------------------------------------------+
| WHERE | Log-reading tools, data pipelines, tools that read          |
|       | messages sent between programs.                              |
+-------+---------------------------------------------------------+
| WHO   | People working with large amounts of incoming data.         |
+-------+---------------------------------------------------------+
| HOW   | In Rust, a piece of text you slice out is really just "a   |
|       | starting point plus a length" pointing INTO the original    |
|       | text — no copy needed. In Python, splitting a line of text  |
|       | always builds brand new pieces of text.                      |
+-------+---------------------------------------------------------+
```

## Part B — the idea in one picture

```
   original text  :  1,ERROR,user9,45
                      ^ ^^^^^ ^^^^^ ^^
   Rust's way    :  just remembers "starts here, this many          |
                     characters long" — pointing INTO the original    |
                     text. "ERROR" = starts at character 2, 5 long.   |
                     No new memory used at all.                        |

   Python's way  :  "1"  "ERROR"  "user9"  "45"  — 4 brand new pieces |
                     of text, each one a fresh copy
```

## Part C — Python vs Rust, step by step

```
             PYTHON                              RUST
+------------------------------+   +------------------------------+
| 1) A big chunk of text is in |   | 1) A big chunk of text is in |
|    memory                     |   |    memory                     |
+------------------------------+   +------------------------------+
               v                                  v
+------------------------------+   +------------------------------+
| 2) Splitting the line builds  |   | 2) Splitting the line gives  |
|    brand NEW pieces of text    |   |    back "start point +        |
+------------------------------+   |    length" markers pointing    |
               v                   |    INTO the same original text  |
+------------------------------+   +------------------------------+
| 3) Turning a piece into a      |                  v
|    number makes yet another    |   +------------------------------+
|    copy                        |   | 3) The number is read right   |
+------------------------------+   |    out of the original text —  |
               v                   |    no copies made anywhere       |
+------------------------------+   +------------------------------+
| 4) Lots of tiny bits of         |                  |
|    memory get created for       |                  |
|    millions of lines             |                  |
+------------------------------+                  |
               |                                  |
               v                                  v
  RESULT: more memory used,           RESULT: far fewer new
  more time spent                      pieces of memory created
```

In a real test: reading 2,000,000 lines of data took 0.358 seconds in
Python and 0.097 seconds in Rust — about 4 times faster.

## Part D — the plain verdict

```
+-----------------------------------------------------------------+
| WHICH ONE SHOULD YOU PICK?                                      |
+--------+--------------------------------------------------------+
| RUST   | Better for very large streams of data (about 4 times     |
|        | faster in this test).                                    |
+--------+--------------------------------------------------------+
| PYTHON | Fine for moderate-sized files (splitting text in Python  |
|        | is itself already pretty fast), or use a library like     |
|        | pandas or Polars for bigger jobs.                          |
+--------+--------------------------------------------------------+
```

## Part E — a deeper look at why this trick is safe in Rust

Pointing at the middle of someone else's data instead of copying it is
risky in many older languages — if the original data gets thrown away
while you're still pointing at it, your program can crash or read
garbage. Rust makes this same trick safe using a compiler check that
tracks, for every single one of these "pointing into" pieces of text,
exactly how long it's allowed to be used.

```
+-----------------------------------------------------------------+
| WHAT THAT TRACKING ACTUALLY BUYS YOU                              |
+-----------------------------------------------------------------+
| A function that splits a line of text and hands back pieces        |
| that point into that same line, is only allowed to be used         |
| while the original line still exists — the compiler tracks this    |
| and enforces it:                                                    |
|                                                                       |
|   somewhere later in the code...                                    |
|   {                                                                   |
|       create the original line of text HERE                          |
|       split it into pieces that point into it                        |
|   } // the original line of text gets thrown away right here         |
|   try to use those pieces down here // COMPILE ERROR: the original   |
|                                      // text doesn't live long        |
|                                      // enough for this to be safe    |
+-----------------------------------------------------------------+
```

The compiler keeps track, for every single one of these pointing-in
pieces, of exactly which stretch of the program it's allowed to be
used in, and refuses to compile any use of it outside that stretch.
That's what turns "point at someone else's memory instead of copying
it" from a classic bug waiting to happen into something checked ahead
of time and completely safe — while still running exactly as fast as
the risky version, since at the machine level it really is just "a
starting point plus a length."

Python's plain pieces of text can't work this way at all, because in
Python, text is never something your own code can point partway into
— it can only ever hand you a whole, separate, brand new piece of
text. So a fresh copy is the only option Python has, every single
time.

## Try it yourself

```bash
python python/zero_copy_parsing.py
```

```bash
cd rust
cargo run --release
```

Both programs read through 2,000,000 lines of comma-separated data
and add up one column of numbers.
