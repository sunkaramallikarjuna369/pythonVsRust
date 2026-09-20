# 14. Where Each Language's Programs Are Able To Run

This is about which devices, operating systems, and environments your
finished program can actually run on.

## Part A — the basics

```
+-----------------------------------------------------------------+
| WHAT IS IT?                                                     |
+-------+---------------------------------------------------------+
| WHAT  | Which devices, operating systems, and environments your    |
|       | program is able to run on.                                   |
+-------+---------------------------------------------------------+
| WHY   | More places it can run means more people can use it.         |
|       | Small devices don't have room for a heavy program-reader.    |
+-------+---------------------------------------------------------+
| WHEN  | When you're targeting web browsers, phones, tiny devices,     |
|       | edge servers (small servers placed close to users), or        |
|       | different kinds of computer chips.                             |
+-------+---------------------------------------------------------+
| WHERE | Running inside web browsers, tiny embedded devices, edge       |
|       | servers, regular servers.                                       |
+-------+---------------------------------------------------------+
| WHO   | People building products and embedded devices.                  |
+-------+---------------------------------------------------------+
| HOW   | Rust turns your code into raw instructions for many            |
|       | different kinds of computer chips, including a special         |
|       | format that runs inside web browsers, and even tiny devices    |
|       | with almost no memory. Python needs its own program-reader     |
|       | installed wherever it runs (there are cut-down versions for    |
|       | browsers and tiny devices, but they're limited).                |
+-------+---------------------------------------------------------+
```

## Part B — the idea in one picture

```
                        +--> Windows / Linux / macOS computers
   One Rust source ------+--> phone chips, Raspberry Pi, etc.
   file, many targets    +--> a format that runs inside web browsers
                        +--> tiny embedded chips with barely any memory

   Python: its own program-reader has to already exist wherever it runs.
```

## Part C — Python vs Rust, step by step

```
             PYTHON                              RUST
+------------------------------+   +------------------------------+
| 1) Needs Python's own          |   | 1) Same Rust source file      |
|    program-reader already       |   +------------------------------+
|    installed                    |                  v
+------------------------------+   +------------------------------+
               v                   | 2) Pick which kind of computer  |
+------------------------------+   |    chip / environment to build   |
| 2) On regular servers and       |   |    for                            |
|    computers: works fine         |   +------------------------------+
+------------------------------+                  v
               v                   +------------------------------+
+------------------------------+   | 3) Runs inside web browsers,      |
| 3) In a web browser: needs a    |   |    on edge servers, on tiny       |
|    heavy extra tool just to      |   |    embedded devices, and on       |
|    run Python at all              |   |    regular servers                 |
+------------------------------+   +------------------------------+
               v                                  |
+------------------------------+                  |
| 4) On tiny devices: only a       |                  |
|    stripped-down, limited          |                  |
|    version of Python works at       |                  |
|    all                               |                  |
+------------------------------+                  |
               |                                  |
               v                                  v
  RESULT: limited reach                  RESULT: runs in places
                                          Python simply can't
```

This is about how many places it can run, not a speed test.

## Part D — the plain verdict

```
+-----------------------------------------------------------------+
| WHICH ONE SHOULD YOU PICK?                                      |
+--------+--------------------------------------------------------+
| RUST   | Better when you need to reach web browsers, edge          |
|        | servers, or tiny embedded devices.                         |
+--------+--------------------------------------------------------+
| PYTHON | Fine for regular servers and computers.                    |
+--------+--------------------------------------------------------+
```

## Part E — a deeper look at why Rust can reach so many more places

The difference in reach comes down to what each "place" actually
needs in order to run the finished program at all — and how little
Rust's version needs.

```
+-----------------------------------------------------------------+
| WHAT EACH KIND OF PLACE NEEDS, JUST TO RUN THE PROGRAM            |
+-----------------------------------------------------------------+
| A regular computer  : just needs an operating system, to handle   |
|                        basic requests like opening files.          |
|                                                                       |
| A web browser        : needs whatever can run a special, compact    |
|                        instruction format that all major browsers    |
|                        understand — Rust can be built straight       |
|                        into that format.                              |
|                                                                       |
| A tiny embedded chip : needs almost nothing — Rust can be built       |
|                        to bring along only a bare-minimum set of       |
|                        basic tools, with no operating system and       |
|                        often no extra memory-management system         |
|                        required at all.                                 |
+-----------------------------------------------------------------+
| All three come from the exact SAME Rust source file — only the      |
| very last step (turning it into raw instructions) changes depending  |
| on where it needs to run.                                             |
+-----------------------------------------------------------------+
```

Python's reach problem is more fundamental than a missing tool:
running a `.py` file means running the full Python program-reader (a
large, complex piece of software implementing the whole language)
somewhere first. A web browser can't just run that kind of software
directly, so tools that let Python run in a browser instead compile
the *entire Python program-reader itself* into the browser's special
instruction format — meaning you end up shipping a whole program-reader
plus your script, not just your script. A tiny embedded device with
barely any memory has no room for that program-reader at all, which is
why cut-down, from-scratch reimplementations of Python exist for those
devices, with far fewer features than regular Python.

Rust never needs to ship a program-reader, because there isn't one to
ship: all of the checking, safety-proving, and speeding-up work already
happened on your own computer while building the program. What
actually gets sent to the tiny device is just the leftover raw
instructions — nothing extra is needed to make sense of them beyond
what the chip itself already provides.

## Try it yourself

```bash
python python/note.py
```

Prints what your own computer needs in order to run Python at all,
and what web browsers or tiny embedded devices would additionally
need.

```bash
cd rust
cargo run --release
```

Runs a small, portable function normally. To see the same code built
for a web browser instead:

```bash
rustup target add wasm32-unknown-unknown
cargo build --release --target wasm32-unknown-unknown
```
