# 7. Handling Things That Go Wrong

This is about how a program reports and reacts when something fails —
bad input, a missing file, the internet being down.

## Part A — the basics

```
+-----------------------------------------------------------------+
| WHAT IS IT?                                                     |
+-------+---------------------------------------------------------+
| WHAT  | How a program reports and reacts when something fails    |
|       | (bad input, a missing file, the network being down).      |
+-------+---------------------------------------------------------+
| WHY   | A failure nobody deals with crashes the program. A       |
|       | failure that gets silently ignored gives wrong results.    |
+-------+---------------------------------------------------------+
| WHEN  | Any action that can fail: reading text as a number,       |
|       | opening files, talking to the network, talking to a        |
|       | database.                                                   |
+-------+---------------------------------------------------------+
| WHERE | Data pipelines, background services, command-line tools.   |
+-------+---------------------------------------------------------+
| WHO   | Every developer. Users experience this as crashes.         |
+-------+---------------------------------------------------------+
| HOW   | Python "throws" a special error object that isn't          |
|       | mentioned anywhere in the function's own description.      |
|       | Rust functions instead openly return either "it worked,     |
|       | here's the answer" or "it failed, here's why" — and you     |
|       | must deal with one or the other.                            |
+-------+---------------------------------------------------------+
```

## Part B — the idea in one picture

```
   Python's way:  try to read "abc" as a number --X--> throws an error
                  the error flies UP through the program looking for
                  a spot that catches it (or the program crashes)

   Rust's way:    try to read "abc" as a number ------> comes back
                  as either "worked: 42" or "failed: bad text"
                  the caller must check which one it got
```

## Part C — Python vs Rust, step by step

```
             PYTHON                              RUST
+------------------------------+   +------------------------------+
| 1) Try to turn "abc" into a  |   | 1) Try to turn "abc" into a  |
|    number                     |   |    number                     |
+------------------------------+   +------------------------------+
               v                                  v
+------------------------------+   +------------------------------+
| 2) Throws an error (this      |   | 2) Comes back as either       |
|    fact isn't written         |   |    "worked" or "failed" —     |
|    anywhere in the function's |   |    right there in what the    |
|    own description)            |   |    function returns            |
+------------------------------+   +------------------------------+
               v                                  v
+------------------------------+   +------------------------------+
| 3) It flies up through the    |   | 3) The caller must check it,  |
|    program looking for a       |   |    or pass it further up on   |
|    "catch" spot                |   |    purpose                     |
+------------------------------+   +------------------------------+
               v                                  v
+------------------------------+   +------------------------------+
| 4) No "catch" spot found:     |   | 4) A failure is just a         |
|    the program CRASHES         |   |    normal, plain value — no    |
|                                 |   |    special handling needed      |
+------------------------------+   +------------------------------+
               |                                  |
               v                                  v
  RESULT: slow when failures          RESULT: fast, obvious, and
  happen a lot                         impossible to just ignore
```

In a real test: parsing 2,000,000 values where half were bad took
1.020 seconds in Python and only 0.011 seconds in Rust — about 90
times faster.

## Part D — the plain verdict

```
+-----------------------------------------------------------------+
| WHICH ONE SHOULD YOU PICK?                                      |
+--------+--------------------------------------------------------+
| RUST   | Better when failures happen often (about 90 times       |
|        | faster in this test), or when a missed failure would    |
|        | be very costly.                                          |
+--------+--------------------------------------------------------+
| PYTHON | Fine and easy to read when failures are rare.            |
+--------+--------------------------------------------------------+
```

## Part E — a deeper look at why handling failures is so much cheaper in Rust

This isn't really about Python's error-throwing being "slow" in
general — it's that Python and Rust do very different amounts of work
on the failure path.

```
+-----------------------------------------------------------------+
| WHAT PYTHON DOES WHEN "abc" FAILS TO BECOME A NUMBER              |
+-----------------------------------------------------------------+
| 1) create a brand new error object to describe what went wrong   |
| 2) walk the ENTIRE chain of function calls that led here, and    |
|    write down every single step of it, in case something later   |
|    wants to print it                                              |
| 3) unwind back out through that whole chain of function calls,   |
|    looking for a spot that catches this kind of error, running    |
|    any cleanup code it passes along the way                       |
| 4) a "catch" spot finally handles it                              |
+-----------------------------------------------------------------+
| The deeper the chain of function calls, the more work step 2      |
| and step 3 have to do — and this happens EVERY single time         |
| something fails.                                                   |
+-----------------------------------------------------------------+

+-----------------------------------------------------------------+
| WHAT RUST DOES WHEN THE SAME THING FAILS                          |
+-----------------------------------------------------------------+
| The function just returns a plain value saying "this failed,      |
| here's why" — nothing more.                                        |
|                                                                     |
| Checking it back at the caller is just an ordinary comparison,     |
| exactly like checking "is this number bigger than zero?" — no      |
| walking back through anything, no writing down every step taken   |
| to get here.                                                        |
+-----------------------------------------------------------------+
```

Because a Rust "failed" value is just a normal piece of data — not a
special event that has to travel back up through the program looking
for somewhere to land — passing a failure up to whoever called your
function is also just a normal, instant return, not a special and
costly operation. Python's approach is more flexible (it can run
cleanup code no matter how far up the chain of calls the "catch" spot
is), but that flexibility is exactly what makes every single failure
more expensive to report, even when the "catch" spot is right next
door.

## Try it yourself

```bash
python python/error_handling.py
```

```bash
cd rust
cargo run --release
```

Both programs try to read 2,000,000 pieces of text as whole numbers,
where exactly half of them are not valid numbers.
