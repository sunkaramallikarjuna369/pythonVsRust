# 6. Null Handling

See the glossary in [rust_vs_python_ascii_diagrams_cpu.txt](../rust_vs_python_ascii_diagrams_cpu.txt) if a term below is unfamiliar.

```
+-----------------------------------------------------------------+
| PART A - WHAT IT IS (5W+H)                                      |
+-------+---------------------------------------------------------+
| WHAT  | How a language represents 'there is no value here' (a   |
|       | missing email, a failed lookup).                        |
+-------+---------------------------------------------------------+
| WHY   | A missing value used as if it existed is one of the     |
|       | most common causes of crashes. Null is often called the |
|       | 'billion-dollar mistake'.                               |
+-------+---------------------------------------------------------+
| WHEN  | Looking up keys, reading database fields, parsing       |
|       | input.                                                  |
+-------+---------------------------------------------------------+
| WHERE | JSON/API data, database rows, config files.             |
+-------+---------------------------------------------------------+
| WHO   | Anyone handling real-world, messy data.                 |
+-------+---------------------------------------------------------+
| HOW   | Python returns None silently. Rust wraps the value in   |
|       | an Option that you must open (match / map / unwrap_or)  |
|       | before using it.                                        |
+-------+---------------------------------------------------------+
```

## PART B — the concept in one picture

```
   Python : email -> "a@b.com"  OR  None   (they look the same)
                     calling .lower() on None = CRASH

   Rust   : email -> Some("a@b.com")  OR  None   (a labelled box)
                     you must open the box before using it
```

## PART C — Python vs Rust, step by step

```
             PYTHON                              RUST
+------------------------------+   +------------------------------+
| 1) d.get('email')            |   | 1) map.get("email")          |
|    returns None              |   |    returns an Option         |
+------------------------------+   +------------------------------+
               v                                  v
+------------------------------+   +------------------------------+
| 2) Code calls .lower()       |   | 2) Option is Some(value)     |
|    on that None              |   |    or None                   |
+------------------------------+   +------------------------------+
               v                                  v
+------------------------------+   +------------------------------+
| 3) Works fine... until       |   | 3) Compiler: 'handle None    |
|    that one record arrives   |   |    first, or no build'       |
+------------------------------+   +------------------------------+
               v                                  v
+------------------------------+   +------------------------------+
| 4) CRASH:                    |   | 4) Use match / map /         |
|    AttributeError            |   |    unwrap_or                 |
+------------------------------+   +------------------------------+
               |                                  |
               v                                  v
  RESULT: found at                   RESULT: found at
  RUNTIME (maybe in prod)            COMPILE time
```

Measured: Python crashed after 99,999 users; safe run 0.100 s vs
0.034 s.

## PART D — verdict

```
+-----------------------------------------------------------------+
| WHICH IS BETTER?                                                |
+--------+--------------------------------------------------------+
| RUST   | Better: missing-value crashes are caught before the    |
|        | program runs.                                          |
+--------+--------------------------------------------------------+
| PYTHON | Fine when data is clean, or with type hints + mypy     |
|        | checks.                                                |
+--------+--------------------------------------------------------+
```

## PART E — why Rust wins here (deep dive)

`Option<T>` looks like a convenience wrapper, but two compiler
mechanisms make it both *safe* and *free*:

```
+-----------------------------------------------------------------+
| 1) EXHAUSTIVENESS: the compiler forces you to face both cases    |
+-----------------------------------------------------------------+
| let email: Option<&String> = user.fields.get("email");           |
|                                                                     |
| match email {                                                     |
|     Some(value) => value.to_lowercase(),                          |
|     // forgot the None arm?                                       |
| }                                                                  |
| -> error[E0004]: non-exhaustive patterns: `None` not covered      |
|    COMPILATION STOPS. There is no way to "accidentally" call       |
|    .to_lowercase() on a value that might not exist.                |
+-----------------------------------------------------------------+

+-----------------------------------------------------------------+
| 2) NICHE OPTIMIZATION: the wrapper usually costs 0 extra bytes   |
+-----------------------------------------------------------------+
| size_of::<&String>()         == 8 bytes (a pointer)               |
| size_of::<Option<&String>>() == 8 bytes  <- SAME SIZE             |
|                                                                     |
| Why: a valid reference can never be the null pointer, so the       |
| compiler reuses the all-zero bit pattern (which a real reference   |
| never has) to mean `None`, instead of adding a separate flag byte. |
+-----------------------------------------------------------------+
```

So `Option<T>` isn't "Rust's version of null with extra ceremony" — it
is the *same bits* a nullable pointer would use in C, except the type
system now knows, statically, everywhere that value flows, whether it
might be absent. `match`'s exhaustiveness check (the same mechanism
covered in [08-type-system-enum-match](../08-type-system-enum-match))
is what actually eliminates the bug class: `email.get("email")` in
Python returns a value indistinguishable from a real string until you
call a method on it and it explodes; `Option<&String>` returns a value
the compiler will not let you treat as a string at all until you've
handled the "it might not be there" case explicitly.

## Run it

```bash
python python/null_handling.py
```

Shows the unsafe version crash with `AttributeError` on the one record
missing an email, then the safe version handle all records.

```bash
cd rust
cargo run --release
```

Same data, but the `Option<&String>` match means there is no crash to
demonstrate — the missing-email case is just another branch.
