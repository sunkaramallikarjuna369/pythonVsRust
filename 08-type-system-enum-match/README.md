# 8. Type System (Enum + Match)

See the glossary in [rust_vs_python_ascii_diagrams_cpu.txt](../rust_vs_python_ascii_diagrams_cpu.txt) if a term below is unfamiliar.

```
+-----------------------------------------------------------------+
| PART A - WHAT IT IS (5W+H)                                      |
+-------+---------------------------------------------------------+
| WHAT  | Rules about what kind of data each variable holds and   |
|       | what you may do with it. An enum lists every possible   |
|       | case of something.                                      |
+-------+---------------------------------------------------------+
| WHY   | Catches mistakes early and makes wrong states           |
|       | impossible to build.                                    |
+-------+---------------------------------------------------------+
| WHEN  | While you write code (compile time in Rust; when the    |
|       | line runs in Python).                                    |
+-------+---------------------------------------------------------+
| WHERE | Domain models, state machines, protocol parsers,        |
|       | claim/order lifecycles.                                  |
+-------+---------------------------------------------------------+
| WHO   | Teams with large, long-lived code, and anyone           |
|       | refactoring.                                             |
+-------+---------------------------------------------------------+
| HOW   | Rust checks types and demands that every enum case is   |
|       | handled, before the program exists. Python checks only  |
|       | when the line runs (hints + mypy are optional).          |
+-------+---------------------------------------------------------+
```

## PART B — the concept in one picture

```
   enum Shape  =  exactly ONE of these:
        +--------+     +------+     +----------+
        | Circle |     | Rect |     | Triangle |
        +--------+     +------+     +----------+

   match shape { Circle => ..,  Rect => ..,  Triangle => .. }
   Rust asks: is EVERY box handled?  If not: compile error.
```

## PART C — Python vs Rust, step by step

```
             PYTHON                              RUST
+------------------------------+   +------------------------------+
| 1) shape = {'type': 'tri'}   |   | 1) enum Shape { Circle,      |
+------------------------------+   |    Rect, Triangle }          |
               v                   +------------------------------+
+------------------------------+                  v
| 2) if / elif chain,          |   +------------------------------+
|    forgot the 'tri' case     |   | 2) match MUST cover          |
+------------------------------+   |    every variant             |
               v                   +------------------------------+
+------------------------------+                  v
| 3) Silently returns None     |   +------------------------------+
+------------------------------+   | 3) Missing one =             |
               v                   |    compile ERROR             |
+------------------------------+   +------------------------------+
| 4) Bug shows up later,       |                  v
|    far from the cause        |   +------------------------------+
+------------------------------+   | 4) Add a variant: every      |
               |                   |    match is flagged          |
               |                   +------------------------------+
               |                                  |
               v                                  v
  RESULT: mistakes hide              RESULT: illegal states
  until runtime                      can't be built
```

Measured (5M area() calls): 0.67 s vs 0.006 s.

## PART D — verdict

```
+-----------------------------------------------------------------+
| WHICH IS BETTER?                                                |
+--------+--------------------------------------------------------+
| RUST   | Better for large or critical code where a forgotten    |
|        | case is costly.                                        |
+--------+--------------------------------------------------------+
| PYTHON | Fine for scripts and prototypes; add type hints for    |
|        | bigger code.                                           |
+--------+--------------------------------------------------------+
```

## PART E — why Rust wins here (deep dive)

The benefit isn't just "Rust checks types" — it's a specific compiler
pass called **exhaustiveness checking**, run on every `match`:

```
+-----------------------------------------------------------------+
| WHAT THE COMPILER ACTUALLY DOES WITH `match shape { ... }`      |
+-----------------------------------------------------------------+
| 1) Look up Shape's definition:                                  |
|      Shape = Circle(f64) | Rect(f64,f64) | Triangle(f64,f64)    |
|                                                                   |
| 2) Build the set of "constructors" that must be covered:        |
|      { Circle, Rect, Triangle }                                 |
|                                                                   |
| 3) Walk your match arms, crossing each one off the set:         |
|      Circle => .. ✓        Rect => .. ✓        Triangle => ??   |
|                                                                   |
| 4) Set not empty at the end?                                    |
|      -> error[E0004]: non-exhaustive patterns: `Triangle` not   |
|         covered.  COMPILATION STOPS. The binary is never built. |
+-----------------------------------------------------------------+
```

Why Python can't do this for free: `shape["type"] == "tri"` is a
string comparison against a `dict`. Nothing in the language declares
"these are ALL the possible shapes" — so there is no fixed set for a
checker to compare your `if/elif` chain against. The list of valid
cases only exists in the programmer's head (or a comment), and heads
forget one case eventually.

The second-order effect matters more than the first bug: add a 4th
variant, `Shape::Square`, and **every existing `match` on `Shape` in
the whole codebase** — not just this one — is re-checked and flagged
if it doesn't handle `Square`. Python's `if/elif` chains scattered
across the codebase get no such re-check; each one silently keeps
"working" (returning `None` or a wrong default) until something
notices the wrong output in production.

## Run it

```bash
python python/shapes.py
```

```bash
cd rust
cargo run --release
```

Both compute the area of 5,000,000 mixed shapes; the Python version
also demonstrates the buggy `if/elif` chain silently returning `None`
for the forgotten `triangle` case.
