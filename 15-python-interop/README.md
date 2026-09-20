# 15. Using Rust Code From Inside A Python Program

This is about writing just one small, slow piece of a Python program
in Rust instead, while keeping the rest of the program in Python
exactly as it was.

## Part A — the basics

```
+-----------------------------------------------------------------+
| WHAT IS IT?                                                     |
+-------+---------------------------------------------------------+
| WHAT  | Using Rust code from inside a Python program — a Python     |
|       | library that's actually written in Rust underneath.          |
+-------+---------------------------------------------------------+
| WHY   | Keep all of Python's convenience, but speed up only the      |
|       | one slow part, without rewriting the whole program.            |
+-------+---------------------------------------------------------+
| WHEN  | After you've measured your program and found exactly one      |
|       | slow function that's the bottleneck.                            |
+-------+---------------------------------------------------------+
| WHERE | Heavy number-crunching, reading structured data, checking      |
|       | that data is valid. Some well-known Python tools (Polars,        |
|       | pydantic-core, ruff) are already built this way.                  |
+-------+---------------------------------------------------------+
| WHO   | Python teams who need more speed but don't want to leave        |
|       | Python.                                                            |
+-------+---------------------------------------------------------+
| HOW   | Write the slow function in Rust using a connector tool          |
|       | called "PyO3", build it into a Python-compatible library         |
|       | with a tool called "maturin", then import and use it just         |
|       | like any other Python library.                                     |
+-------+---------------------------------------------------------+
```

## Part B — the idea in one picture

```
   +-------------------------------+
   |  Your Python program           |
   |  (everything else unchanged)   |     +----------------------+
   |   answer = fast_tool.compute(x)|---->| The Rust function     |
   |   ...                          |<----| (runs at native speed)|
   +-------------------------------+     +----------------------+
```

## Part C — Python vs Rust, step by step

```
        PYTHON ON ITS OWN                  PYTHON + RUST TOGETHER
+------------------------------+   +------------------------------+
| 1) Measure the program: find    |   | 1) Rewrite ONLY that ONE     |
|    the one slow function         |   |    function in Rust           |
+------------------------------+   +------------------------------+
               v                                  v
+------------------------------+   +------------------------------+
| 2) The loop runs inside          |   | 2) Build it into a Python-  |
|    Python's own program-reader    |   |    compatible library         |
+------------------------------+   +------------------------------+
               v                                  v
+------------------------------+   +------------------------------+
| 3) That one spot stays slow      |   | 3) Import it in Python,      |
|    no matter what else you do     |   |    exactly like any other     |
+------------------------------+   |    library                     |
               |                   +------------------------------+
               |                                  v
               |                   +------------------------------+
               |                   | 4) Everything else stays        |
               |                   |    unchanged Python — only        |
               |                   |    the slow part is now native     |
               |                   +------------------------------+
               |                                  |
               v                                  v
  RESULT: the slow part stays          RESULT: same Python program,
  slow no matter what                  slow part now runs fast
```

There's no measured number here — this depends on setting up the
connector tool locally first.

## Part D — the plain verdict

```
+-----------------------------------------------------------------+
| WHICH ONE SHOULD YOU PICK?                                      |
+--------+--------------------------------------------------------+
| RUST   | Best of both worlds: rewrite only the slow function,     |
|        | leave everything else alone.                               |
+--------+--------------------------------------------------------+
| PYTHON | Stays the glue holding everything together: keep it for   |
|        | everything that isn't the slow part.                        |
+--------+--------------------------------------------------------+
```

## Part E — a deeper look at why this pairing works so well

The reason this combination works so smoothly is that crossing from
Python into Rust and back barely costs anything — it's mostly just
handing values across, not converting or copying huge amounts of data.

```
+-----------------------------------------------------------------+
| WHAT ACTUALLY HAPPENS WHEN PYTHON CALLS A RUST FUNCTION           |
+-----------------------------------------------------------------+
| 1) Python calls fast_tool.compute(a_list_of_numbers)               |
|         |                                                            |
|         v                                                            |
| 2) A small connector piece, generated automatically by the PyO3     |
|    tool, runs first:                                                 |
|      - reads the Python list directly                                |
|      - turns each Python number into a plain number Rust can use     |
|        (a quick, direct conversion — no new Python objects created)  |
|         |                                                             |
|         v                                                              |
| 3) Your actual Rust code runs at full native speed on those plain    |
|    numbers — everything covered elsewhere in this project (safe       |
|    memory handling, no accidental data corruption between threads,     |
|    and so on) still applies here too                                    |
|         |                                                                |
|         v                                                                |
| 4) The connector piece turns the final answer back into a single       |
|    Python number and hands it back — one conversion for the whole       |
|    answer, not one for every single number involved                      |
+-----------------------------------------------------------------+
```

Two things make this cheaper than, say, running the Rust code as a
totally separate program and talking to it over the network:

1. **They share the exact same running program.** The connector tool
   builds the Rust code directly into the same running Python
   process, exactly like other well-known fast Python libraries do.
   There's no sending data over a network, no separate program to
   start — just a direct function call.
2. **Python's "only one thread at a time" rule can be turned off for
   the Rust part.** A Rust function called from Python can choose to
   temporarily step outside that rule (described in
   [03-parallelism](../03-parallelism)) while it does its own
   heavy lifting — something a plain Python function is never able to
   do on its own.

This is exactly how tools like `pydantic-core`, `ruff`, and `polars`
manage to feel like ordinary, easy Python libraries while running as
fast as native code underneath: the slow inner loop is compiled Rust;
everything else stays comfortable, ordinary Python.

## Try it yourself

```bash
cd rust
pip install maturin
maturin develop --release
```

```bash
cd ../python
python use_fast_mod.py
```

Even without running the `maturin develop` step first, `use_fast_mod.py`
still runs — it will simply report that the Rust version isn't built
yet, and fall back to running the plain Python version instead, so you
can see the "before" result too.
