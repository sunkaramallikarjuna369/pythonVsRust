# 13. Data That Is Not Allowed To Change By Accident

This is about data that, once created, cannot be changed unless you
specifically say it's allowed to be. Data that can't be changed at all
is often called "immutable."

## Part A — the basics

```
+-----------------------------------------------------------------+
| WHAT IS IT?                                                     |
+-------+---------------------------------------------------------+
| WHAT  | Data that cannot change after it's created. In Rust,       |
|       | variables are locked and unchangeable by default, unless   |
|       | you specifically mark them as changeable.                   |
+-------+---------------------------------------------------------+
| WHY   | If nothing can quietly change your data behind your back,  |
|       | "wait, who changed this?" bugs disappear, and sharing        |
|       | data between threads becomes much safer.                     |
+-------+---------------------------------------------------------+
| WHEN  | Whenever you're passing data between functions, or           |
|       | sharing it between threads.                                    |
+-------+---------------------------------------------------------+
| WHERE | Settings, data shared across a program, data pipelines.       |
+-------+---------------------------------------------------------+
| WHO   | Anyone who has ever spent time tracking down a value that     |
|       | changed when they didn't expect it to.                         |
+-------+---------------------------------------------------------+
| HOW   | In Rust, a plain variable is locked by default; you have to   |
|       | explicitly mark it as changeable, and even then only ONE       |
|       | changeable reference to it is allowed to exist at a time. In   |
|       | Python, everything can be changed by default, from anywhere.   |
+-------+---------------------------------------------------------+
```

## Part B — the idea in one picture

```
   Python : x points to [1, 2, 3]   <-- one function can change it
                                    <-- another function can too
                                    Who actually changed it? You'd
                                    have to search the whole program.

   Rust   : a plain variable is LOCKED by default
            a variable marked as changeable may change it — but
            only ONE changeable reference is allowed at a time
```

## Part C — Python vs Rust, step by step

```
             PYTHON                              RUST
+------------------------------+   +------------------------------+
| 1) x = [1, 2, 3]               |   | 1) x = [1, 2, 3]              |
+------------------------------+   |    (locked, unchangeable, by  |
               v                   |    default)                     |
+------------------------------+   +------------------------------+
| 2) Any function that receives   |                  v
|    x is free to change it        |   +------------------------------+
+------------------------------+   | 2) Trying to change x is an     |
               v                   |    ERROR, unless you specially   |
+------------------------------+   |    marked it as changeable        |
| 3) The caller's list changed     |   +------------------------------+
|    without them expecting it      |                  v
+------------------------------+   +------------------------------+
               v                   | 3) A changeable reference: only  |
+------------------------------+   |    ONE writer allowed at a time   |
| 4) Classic trap: a shared,        |   +------------------------------+
|    reused default value that       |                  |
|    quietly builds up over time      |                  |
+------------------------------+                  |
               |                                  |
               v                                  v
  RESULT: surprising, unwanted            RESULT: changes are always
  side effects                            obvious and on purpose
```

This is a "does it behave correctly" comparison, not a speed test.

## Part D — the plain verdict

```
+-----------------------------------------------------------------+
| WHICH ONE SHOULD YOU PICK?                                      |
+--------+--------------------------------------------------------+
| RUST   | Better when you want the compiler itself to enforce      |
|        | this rule for you.                                        |
+--------+--------------------------------------------------------+
| PYTHON | Fine as long as you build good habits: use fixed-size     |
|        | tuples, "frozen" data types, or make copies on purpose.    |
+--------+--------------------------------------------------------+
```

## Part E — a deeper look at the rule the Rust compiler enforces here

Underneath "locked by default vs. changeable," there's one single rule
that also shows up in [04-data-race-safety](../04-data-race-safety):
at any moment, the compiler only allows either

```
+-----------------------------------------------------------------+
| THE RULE THE COMPILER ENFORCES                                    |
+-----------------------------------------------------------------+
|   many read-only "just looking" references       OR   exactly one |
|   at the same piece of data                            changeable |
|                                                          reference  |
|                                                                       |
|   ... but NEVER both kinds at the same time.                         |
+-----------------------------------------------------------------+
| x = [1, 2, 3], marked as changeable                                 |
| a = a read-only look at x     // fine: just looking                 |
| b = another read-only look    // also fine: still just looking      |
| try to add a new item to x    // ERROR: can't change x while         |
|                                // something is still just looking     |
|                                // at it                                 |
| use "a" down here             // "a" is still expected to be valid   |
|                                // here — the change above would        |
|                                // have broken that                     |
+-----------------------------------------------------------------+
```

The compiler works out, for every single reference, exactly which
stretch of code it's used in, then refuses to let a "changeable"
stretch overlap with any other stretch touching the same data. This
check happens once, while reading through your code before it's even
built — there's no locking or checking of any kind while the program
is actually running, so correct code pays absolutely nothing extra for
this guarantee.

Compare that to Python: a list handed into a function carries no
marker at all saying whether that function plans to just look at it or
actually change it. The only way to know is to go read that function's
own code (or its notes, if it has any) — the language gives you
nothing to check against ahead of time, so "wait, who changed this?"
is always a manual hunt, never something the computer catches for you.

## Try it yourself

```bash
python python/immutability.py
```

Shows the classic "shared, reused default value" trap, and a function
that changes a list without the caller expecting it.

```bash
cd rust
cargo run --release
```

Shows locked vs. changeable variables, and a function whose own
description openly says it's allowed to change what you hand it.
