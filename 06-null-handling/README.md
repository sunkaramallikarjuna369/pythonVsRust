# 6. Handling "No Value Here" Without Crashing

This is about how a language deals with the idea of "there is nothing
here" — like a missing email address, or a search that found nothing.

## Part A — the basics

```
+-----------------------------------------------------------------+
| WHAT IS IT?                                                     |
+-------+---------------------------------------------------------+
| WHAT  | How a language represents "there is no value here" (a    |
|       | missing email address, a search that found nothing).     |
+-------+---------------------------------------------------------+
| WHY   | Trying to use a missing value as if it were real is one   |
|       | of the most common causes of crashes in software.         |
+-------+---------------------------------------------------------+
| WHEN  | Looking things up, reading fields from a database,        |
|       | reading in outside data.                                   |
+-------+---------------------------------------------------------+
| WHERE | Data coming from other websites/services, database rows,  |
|       | settings files.                                            |
+-------+---------------------------------------------------------+
| WHO   | Anyone dealing with real-world, messy data.                |
+-------+---------------------------------------------------------+
| HOW   | Python just gives you a special "nothing" value (called    |
|       | "None") and quietly lets you try to use it anyway. Rust    |
|       | wraps every "might be missing" value in a labelled box     |
|       | that you are FORCED to open and check before you're        |
|       | allowed to use what's inside.                              |
+-------+---------------------------------------------------------+
```

## Part B — the idea in one picture

```
   Python : email is either "a@b.com" OR "nothing" — and they look
            exactly the same until you try to use it.
            Trying to use the "nothing" one as text = CRASH

   Rust   : email is a labelled box: "has a value: a@b.com" OR
            "empty box". You must open the box and check which
            kind it is before you're allowed to use what's inside.
```

## Part C — Python vs Rust, step by step

```
             PYTHON                              RUST
+------------------------------+   +------------------------------+
| 1) Look up "email" in a      |   | 1) Look up "email" — you get |
|    record, get "nothing"      |   |    back a labelled box, not   |
|    back                       |   |    the value directly         |
+------------------------------+   +------------------------------+
               v                                  v
+------------------------------+   +------------------------------+
| 2) Code calls a text method  |   | 2) The box either "has a      |
|    on that "nothing" value    |   |    value" or is "empty"       |
+------------------------------+   +------------------------------+
               v                                  v
+------------------------------+   +------------------------------+
| 3) Works fine for a while...  |   | 3) The compiler says:         |
|    until that one record       |   |    "handle the empty case     |
|    arrives                     |   |    first, or this won't       |
+------------------------------+   |    build"                     |
               v                   +------------------------------+
+------------------------------+                  v
| 4) CRASH: tried to use a       |   +------------------------------+
|    "nothing" value as text     |   | 4) So you handle both cases  |
+------------------------------+   |    on purpose                  |
               |                   +------------------------------+
               |                                  |
               v                                  v
  RESULT: found out only when          RESULT: found out before
  the program is actually running       the program can even run
  (maybe after it's already live)
```

In a real test: the Python version crashed right after processing
99,999 good records when it hit one bad one; a version that safely
checked for "nothing" first took 0.100 seconds compared to Rust's
0.034 seconds, with no crash possible in Rust at all.

## Part D — the plain verdict

```
+-----------------------------------------------------------------+
| WHICH ONE SHOULD YOU PICK?                                      |
+--------+--------------------------------------------------------+
| RUST   | Better: missing-value crashes are caught before the     |
|        | program is even allowed to run.                          |
+--------+--------------------------------------------------------+
| PYTHON | Fine when the data is clean, or if you add extra type    |
|        | checking tools to catch this earlier.                    |
+--------+--------------------------------------------------------+
```

## Part E — a deeper look at why Rust's "labelled box" idea works so well

That labelled box (its real name is "Option") sounds like it should
slow things down or use extra memory — but two things make it both
safe AND free:

```
+-----------------------------------------------------------------+
| 1) YOU CAN'T FORGET TO CHECK                                     |
+-----------------------------------------------------------------+
| When you open the labelled box, the compiler makes you handle    |
| BOTH possible outcomes — "there's a value" and "it's empty" —    |
| or it flat out refuses to build the program. There's no way to   |
| accidentally skip the "what if it's empty?" case.                 |
+-----------------------------------------------------------------+

+-----------------------------------------------------------------+
| 2) THE BOX USUALLY COSTS NOTHING EXTRA                            |
+-----------------------------------------------------------------+
| A normal reference to some text takes up, say, 8 bytes of        |
| memory. The "labelled box" version of that same reference ALSO   |
| takes up exactly 8 bytes — not one byte more.                    |
|                                                                    |
| Why: a real, valid reference can never happen to be the special   |
| "points at nothing at all" pattern, so Rust just reuses that      |
| otherwise-impossible pattern to mean "empty box" — instead of      |
| tacking on an extra marker.                                       |
+-----------------------------------------------------------------+
```

So this "labelled box" isn't really Rust adding paperwork on top of
Python's "nothing" value — under the hood, it can literally be stored
using the exact same bits a plain "empty" marker would use. The real
difference is that the compiler now knows, everywhere that value
travels through your program, whether it might be empty — and refuses
to let you use it without checking first. Python's version returns a
value that looks completely normal until you try to use it and it
blows up; Rust's version simply won't let your code compile until
you've dealt with the empty case on purpose.

## Try it yourself

```bash
python python/null_handling.py
```

```bash
cd rust
cargo run --release
```

Both programs process 100,000 fake user records, one of which is
deliberately missing its email address.
