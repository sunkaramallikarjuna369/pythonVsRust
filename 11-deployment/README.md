# 11. Getting Your Program Running On Another Computer

This is about what it takes to move your finished program from your
own computer onto a server, a container, or someone else's computer,
and get it running there.

## Part A — the basics

```
+-----------------------------------------------------------------+
| WHAT IS IT?                                                     |
+-------+---------------------------------------------------------+
| WHAT  | Getting your program from your own computer to run          |
|       | somewhere else: a server, a packaged container, or a         |
|       | customer's computer.                                          |
+-------+---------------------------------------------------------+
| WHY   | More separate pieces means more things that can break,       |
|       | bigger packages to send around, and slower start-up times.    |
+-------+---------------------------------------------------------+
| WHEN  | Every time you release a new version, and especially for     |
|       | small on-demand functions that start up often.                |
+-------+---------------------------------------------------------+
| WHERE | Packaged containers (like Docker), cloud services that        |
|       | run your code on demand, tools you hand to other people.       |
+-------+---------------------------------------------------------+
| WHO   | People who manage servers, and anyone shipping software.      |
+-------+---------------------------------------------------------+
| HOW   | For Python, you need to ship the Python program-reader        |
|       | itself, plus an isolated set of installed libraries, plus     |
|       | your own code. For Rust, you build one single file and just    |
|       | copy that.                                                     |
+-------+---------------------------------------------------------+
```

## Part B — the idea in one picture

```
   What you need to ship for Python:      What you need to ship
                                           for Rust:
   +---------------------------+          +----------------+
   | The Python program-reader |          |                |
   | An isolated set of        |          | ONE single     |
   |   installed libraries      |          | file           |
   | Your own .py code           |          |                |
   +---------------------------+          +----------------+
```

## Part C — Python vs Rust, step by step

```
             PYTHON                              RUST
+------------------------------+   +------------------------------+
| 1) Install the right          |   | 1) Build the program in       |
|    version of Python            |   |    "release" mode              |
+------------------------------+   +------------------------------+
               v                                  v
+------------------------------+   +------------------------------+
| 2) Set up an isolated space    |   | 2) Get back ONE single file  |
|    for that project's           |   |    (everything it needs is    |
|    libraries                    |   |    already built in)           |
+------------------------------+   +------------------------------+
               v                                  v
+------------------------------+   +------------------------------+
| 3) Install every library the   |   | 3) Copy it over, run it       |
|    project needs                |   |    (starts in about 1         |
+------------------------------+   |    thousandth of a second)      |
               v                   +------------------------------+
+------------------------------+                  |
| 4) Ship the code plus the       |                  |
|    isolated space, then start   |                  |
|    the program-reader (about     |                  |
|    9 thousandths of a second)   |                  |
+------------------------------+                  |
               |                                  |
               v                                  v
  RESULT: several separate            RESULT: one file, a tiny
  moving pieces                       package overall
```

In a real test: starting up took about 9.34 thousandths of a second in
Python versus 0.91 thousandths of a second in Rust; the Rust "hello
world" file came out to about 338 KB in total.

## Part D — the plain verdict

```
+-----------------------------------------------------------------+
| WHICH ONE SHOULD YOU PICK?                                      |
+--------+--------------------------------------------------------+
| RUST   | Better for tiny packages, fast start-up, and tools you   |
|        | hand off to other people.                                 |
+--------+--------------------------------------------------------+
| PYTHON | Fine when your packaging tools already manage the setup   |
|        | for you.                                                   |
+--------+--------------------------------------------------------+
```

## Part E — a deeper look at why Rust starts up so much faster

The gap comes down to *when* the heavy lifting happens: while you're
building the program, versus every single time it starts up.

```
+-----------------------------------------------------------------+
| WHAT HAPPENS THE INSTANT YOU RUN THE PROGRAM                     |
+-----------------------------------------------------------------+
| Rust's single file:                                                |
|   the operating system loads the file into memory                  |
|   -> jumps straight to the start of your program (everything it    |
|      needs was already figured out and packed in while it was      |
|      being built, on your own computer)                             |
|   -> about 1 thousandth of a second                                 |
|                                                                       |
| Python script:                                                     |
|   the operating system starts the Python program-reader              |
|   -> the reader sets itself up: builds its own internal systems,     |
|      loads its own built-in library files, sets up its background    |
|      memory helper                                                   |
|   -> it then finds and loads every library YOUR code depends on      |
|      from disk, and each one of those runs its OWN start-up code     |
|   -> only THEN does it actually start running your program            |
|   -> about 9 thousandths of a second, and it grows the more           |
|      libraries you add                                                |
+-----------------------------------------------------------------+
```

Rust does all of its "figuring out where everything is" work once,
while you're building the program on your own computer, producing a
single file that already knows exactly what to do and where everything
is. Python puts almost all of that figuring-out off until the program
actually starts running — it re-discovers what every library contains,
fresh, every single time, because nothing was worked out and locked in
ahead of time. That's also why a Rust file can just be copied to
another computer and run right away: there's no "is the right version
of the program-reader installed, with the right libraries?" question
left to go wrong.

## Try it yourself

```bash
python python/hello.py
```

```bash
cd rust
cargo build --release
./target/release/hello
```

Time either one with your terminal's built-in timing tool to compare
how quickly each one starts up.
