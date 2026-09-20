# 8. Making Sure Every Possible Case Is Actually Handled

This is about how strictly a language checks what kind of data a
variable holds, and what you're allowed to do with it. A "list of
every possible case something could be" (for example: a shape is
either a circle, a rectangle, or a triangle, and nothing else) is
sometimes called an "enum" for short.

## Part A — the basics

```
+-----------------------------------------------------------------+
| WHAT IS IT?                                                     |
+-------+---------------------------------------------------------+
| WHAT  | Rules about what kind of data each variable can hold,     |
|       | and what you're allowed to do with it. A "list of every   |
|       | possible case" spells out all the options up front.        |
+-------+---------------------------------------------------------+
| WHY   | Catches mistakes early, and makes it impossible to build   |
|       | a piece of data that isn't one of the allowed cases.        |
+-------+---------------------------------------------------------+
| WHEN  | While you write code, in Rust's case — checked before the  |
|       | program even runs. In Python, only when that exact line    |
|       | of code actually runs.                                      |
+-------+---------------------------------------------------------+
| WHERE | Business rules, step-by-step processes, reading structured |
|       | messages, order/claim lifecycles.                           |
+-------+---------------------------------------------------------+
| WHO   | Teams with large, long-lasting code, and anyone changing    |
|       | old code later.                                              |
+-------+---------------------------------------------------------+
| HOW   | Rust checks types AND demands that every single listed      |
|       | case is actually dealt with, before the program even        |
|       | exists. Python only checks things as each line actually      |
|       | runs (extra tools can check ahead of time, but they're       |
|       | optional).                                                   |
+-------+---------------------------------------------------------+
```

## Part B — the idea in one picture

```
   A Shape is EXACTLY ONE of these, and nothing else:
        +--------+     +------+     +----------+
        | Circle |     | Rect |     | Triangle |
        +--------+     +------+     +----------+

   When you handle a shape, Rust asks: "did you cover EVERY box?"
   If not: the program won't build at all.
```

## Part C — Python vs Rust, step by step

```
             PYTHON                              RUST
+------------------------------+   +------------------------------+
| 1) shape = {"type": "tri"}   |   | 1) A shape is EXACTLY one of |
+------------------------------+   |    Circle, Rect, or Triangle  |
               v                   +------------------------------+
+------------------------------+                  v
| 2) A chain of "if this,      |   +------------------------------+
|    else if that" checks —     |   | 2) Handling a shape MUST      |
|    accidentally forgot the    |   |    cover every listed case    |
|    triangle case               |   +------------------------------+
+------------------------------+                  v
               v                   +------------------------------+
+------------------------------+   | 3) Forgot one case? The       |
| 3) Quietly returns "nothing"  |   |    program simply won't       |
+------------------------------+   |    build                       |
               v                   +------------------------------+
+------------------------------+                  v
| 4) The bug only shows up      |   +------------------------------+
|    later, far from where it   |   | 4) Add a new shape later:     |
|    was actually caused         |   |    every place handling       |
+------------------------------+   |    shapes gets flagged          |
               |                   +------------------------------+
               |                                  |
               v                                  v
  RESULT: mistakes stay hidden        RESULT: it's simply not
  until the program is running        possible to forget a case
```

In a real test: calculating the area of 5,000,000 shapes took 0.67
seconds in Python and only 0.006 seconds in Rust.

## Part D — the plain verdict

```
+-----------------------------------------------------------------+
| WHICH ONE SHOULD YOU PICK?                                      |
+--------+--------------------------------------------------------+
| RUST   | Better for large or important code, where forgetting a  |
|        | case would be costly.                                    |
+--------+--------------------------------------------------------+
| PYTHON | Fine for quick scripts and early drafts; add extra type  |
|        | checking tools once the code grows bigger.                |
+--------+--------------------------------------------------------+
```

## Part E — a deeper look at how Rust actually checks "every case is covered"

This isn't just Rust "being strict" — it's a specific, automatic check
the compiler runs every time you handle one of these "exactly one of
these options" values:

```
+-----------------------------------------------------------------+
| WHAT THE COMPILER ACTUALLY DOES WHEN YOU HANDLE A SHAPE           |
+-----------------------------------------------------------------+
| 1) Look up the full, official list of what a Shape can be:        |
|      Circle, Rect, Triangle — and nothing else                    |
|                                                                     |
| 2) Go through your code's handling of shapes, and cross each      |
|    case off the list as it finds it handled:                       |
|      Circle: handled ✓     Rect: handled ✓     Triangle: ??       |
|                                                                     |
| 3) Anything left un-crossed at the end?                            |
|      -> stop right there and report exactly which case was         |
|         missed. The program is never built at all.                 |
+-----------------------------------------------------------------+
```

Python can't do this same check for free, because `shape["type"] ==
"triangle"` is just comparing plain text against a plain dictionary.
Nothing in the language ever declares "these are ALL the shapes that
will ever exist" — so there's no official list for anything to check
your chain of "if this, else if that" against. That official list only
lives in the programmer's memory (or maybe a comment), and memory
fades.

The bigger payoff shows up later: add a 4th shape, say `Square`, and
Rust will recheck *every single place in the whole project* that
handles shapes, and flag every one that doesn't yet handle `Square`
too. Python's scattered "if this, else if that" chains get no such
recheck — each one keeps quietly "working" (returning nothing, or a
wrong default) until someone notices the wrong output, possibly long
after the new shape was added.

## Try it yourself

```bash
python python/shapes.py
```

```bash
cd rust
cargo run --release
```

Both programs calculate the total area of 5,000,000 mixed shapes; the
Python version also shows the buggy version quietly returning
"nothing" for the shape type it forgot to handle.
