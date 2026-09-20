# 7. Error Handling

See the glossary in [rust_vs_python_ascii_diagrams_cpu.txt](../rust_vs_python_ascii_diagrams_cpu.txt) if a term below is unfamiliar.

```
+-----------------------------------------------------------------+
| PART A - WHAT IT IS (5W+H)                                      |
+-------+---------------------------------------------------------+
| WHAT  | How a program reports and reacts when something fails   |
|       | (bad input, missing file, network down).                |
+-------+---------------------------------------------------------+
| WHY   | An unhandled failure crashes the program. A hidden      |
|       | failure gives wrong results.                            |
+-------+---------------------------------------------------------+
| WHEN  | Any operation that can fail: parsing, files, network,   |
|       | databases.                                              |
+-------+---------------------------------------------------------+
| WHERE | Pipelines, services, command-line tools.                |
+-------+---------------------------------------------------------+
| WHO   | Every developer. Users feel it as crashes.              |
+-------+---------------------------------------------------------+
| HOW   | Python throws exceptions (not shown in the function     |
|       | signature). Rust returns a Result: Ok(value) or         |
|       | Err(reason), which you handle or pass on with ?.        |
+-------+---------------------------------------------------------+
```

## PART B — the concept in one picture

```
   Python (exception):  parse() --X--> raises an error
                        it flies UP the call stack to a try/except
                        catches it (or the program crashes)

   Rust (Result):       parse() ------> returns Ok(42) / Err("bad")
                        the caller matches on it, or uses ?
```

## PART C — Python vs Rust, step by step

```
             PYTHON                              RUST
+------------------------------+   +------------------------------+
| 1) int('abc')                |   | 1) "abc".parse::<u32>()      |
+------------------------------+   +------------------------------+
               v                                  v
+------------------------------+   +------------------------------+
| 2) Raises ValueError         |   | 2) Returns a Result:         |
|    (not visible in the       |   |    Ok(n) or Err(e)           |
|    function signature)       |   +------------------------------+
+------------------------------+                  v
               v                   +------------------------------+
+------------------------------+   | 3) Caller must match it      |
| 3) Flies up the call stack   |   |    or pass it on with ?      |
|    to a try/except           |   +------------------------------+
+------------------------------+                  v
               v                   +------------------------------+
+------------------------------+   | 4) Error is just a normal    |
| 4) None found: program       |   |    value, no unwinding       |
|    CRASHES                   |   +------------------------------+
+------------------------------+                  |
               |                                  |
               v                                  v
  RESULT: slow when errors           RESULT: fast, explicit,
  are common                         cannot be ignored
```

Measured (1M bad of 2M values): 1.020 s vs 0.011 s = ~90x.

## PART D — verdict

```
+-----------------------------------------------------------------+
| WHICH IS BETTER?                                                |
+--------+--------------------------------------------------------+
| RUST   | Better when errors are common (about 90x in my test)   |
|        | or must never be missed.                               |
+--------+--------------------------------------------------------+
| PYTHON | Fine and readable when errors are rare.                |
+--------+--------------------------------------------------------+
```

## PART E — why Rust wins here (deep dive)

The 90x isn't really "exceptions are slow" in the abstract — it's that
Python's exceptions and Rust's `Result` pay for fundamentally different
amounts of machinery on the *success* path and the *failure* path.

```
+-----------------------------------------------------------------+
| WHAT A PYTHON EXCEPTION COSTS WHEN "abc" FAILS TO PARSE           |
+-----------------------------------------------------------------+
| int("abc")                                                        |
|   -> raises ValueError: allocate an exception object              |
|   -> capture a traceback: walk and record the ENTIRE call stack   |
|      (every frame, every line number) into a linked structure     |
|   -> unwind the C stack looking for a matching `except` handler,  |
|      running `finally` blocks along the way                       |
|   -> the `except ValueError:` handler finally catches it           |
+-----------------------------------------------------------------+
| Cost is proportional to how DEEP the call stack is - a stack       |
| search happens on every single failure.                            |
+-----------------------------------------------------------------+

+-----------------------------------------------------------------+
| WHAT `"abc".parse::<u32>()` COSTS WHEN IT FAILS                  |
+-----------------------------------------------------------------+
| fn parse(s: &str) -> Result<u32, ParseIntError> {                 |
|     ...                                                            |
|     Err(ParseIntError { kind: InvalidDigit })   // just a value!  |
| }                                                                   |
|                                                                     |
| match v.parse::<u32>() {                                           |
|     Ok(_)  => ok += 1,                                             |
|     Err(_) => bad += 1,   // a normal branch, like `if`             |
| }                                                                   |
+-----------------------------------------------------------------+
| No stack walk, no unwinding, no separate control-flow mechanism -  |
| `Result` IS the return value, checked with an ordinary branch.     |
+-----------------------------------------------------------------+
```

This is also why Rust's `?` operator is "free" in the same sense: `x?`
desugars to "if `x` is `Err`, `return Err(...)` immediately" — a
regular conditional jump, not a throw. Python's exception mechanism
has to stay general enough to unwind through arbitrary call depths and
run cleanup code along the way, which is powerful but means every
`raise` pays for a stack walk whether the catcher is one frame up or
fifty.

## Run it

```bash
python python/error_handling.py
```

```bash
cd rust
cargo run --release
```

Both parse 2,000,000 strings where half are valid integers and half
are not, counting `ok`/`bad` and timing the whole pass — Python pays
per-exception cost, Rust's `Result` does not.
