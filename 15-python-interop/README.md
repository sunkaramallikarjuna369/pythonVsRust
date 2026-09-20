# 15. Python Interop

See the glossary in [rust_vs_python_ascii_diagrams_cpu.txt](../rust_vs_python_ascii_diagrams_cpu.txt) if a term below is unfamiliar.

```
+-----------------------------------------------------------------+
| PART A - WHAT IT IS (5W+H)                                      |
+-------+---------------------------------------------------------+
| WHAT  | Using Rust code from inside a Python program: a Python  |
|       | module written in Rust.                                 |
+-------+---------------------------------------------------------+
| WHY   | Keep Python's convenience and speed up only the slow    |
|       | part, with no full rewrite.                             |
+-------+---------------------------------------------------------+
| WHEN  | You profiled your code and found one hot function.      |
+-------+---------------------------------------------------------+
| WHERE | Number crunching, parsers, validators. Polars,          |
|       | pydantic-core and ruff are Rust-backed.                 |
+-------+---------------------------------------------------------+
| WHO   | Python teams that need speed without leaving Python.    |
+-------+---------------------------------------------------------+
| HOW   | Write the function in Rust with PyO3, build with        |
|       | maturin, then import it like any Python module.         |
+-------+---------------------------------------------------------+
```

## PART B — the concept in one picture

```
   +-------------------------------+
   |  Your Python app (unchanged)  |
   |   ...                         |     +----------------------+
   |   r = fast_mod.compute(data)  |---->| Rust function        |
   |   ...                         |<----| (native, via PyO3)   |
   +-------------------------------+     +----------------------+
```

## PART C — Python vs Rust, step by step

```
          PYTHON ALONE                      PYTHON + RUST
+------------------------------+   +------------------------------+
| 1) Profile: find the slow    |   | 1) Rewrite ONLY that         |
|    function                  |   |    function in Rust          |
+------------------------------+   +------------------------------+
               v                                  v
+------------------------------+   +------------------------------+
| 2) Loop runs in the          |   | 2) Build with maturin        |
|    interpreter               |   |    (PyO3 bindings)           |
+------------------------------+   +------------------------------+
               v                                  v
+------------------------------+   +------------------------------+
| 3) Program stays slow        |   | 3) import fast_mod in        |
|    at that spot              |   |    Python as usual           |
+------------------------------+   +------------------------------+
               |                                  v
               |                   +------------------------------+
               |                   | 4) Rest of code unchanged,   |
               |                   |    hot path runs native      |
               |                   +------------------------------+
               |                                  |
               v                                  v
  RESULT: slow hot path              RESULT: same Python app,
                                     fast hot path
```

(Not measured here: needs PyO3 set up locally.)

## PART D — verdict

```
+-----------------------------------------------------------------+
| WHICH IS BETTER?                                                |
+--------+--------------------------------------------------------+
| RUST   | Best of both: rewrite only the slow function in Rust.  |
+--------+--------------------------------------------------------+
| PYTHON | Python stays the glue: keep it for everything that is  |
|        | not hot.                                                |
+--------+--------------------------------------------------------+
```

## PART E — why Rust wins here (deep dive)

The reason this pairing works so well is that the "bridge" PyO3
generates has almost no cost of its own — the boundary crossing is
mostly bookkeeping, not data conversion.

```
+-----------------------------------------------------------------+
| WHAT `#[pyfunction] fn compute(values: Vec<i64>) -> PyResult<..>`|
| ACTUALLY COMPILES TO                                             |
+-----------------------------------------------------------------+
| 1) Python calls fast_mod.compute(list_of_ints)                  |
|         |                                                        |
|         v                                                        |
| 2) PyO3-generated C-ABI wrapper function runs:                   |
|      - reads the Python list via the C API (PyList_GetItem)      |
|      - converts each PyObject int -> a plain i64 (a memcpy-      |
|        cheap operation, no new Python objects created)           |
|         |                                                        |
|         v                                                        |
| 3) Your actual Rust `compute()` runs at full native speed on a   |
|    plain Vec<i64> - the borrow checker, ownership, and every     |
|    other guarantee elsewhere in this repo still apply HERE       |
|         |                                                        |
|         v                                                        |
| 4) Wrapper converts the i64 result back to a Python int and      |
|    returns it - one allocation, not one per element              |
+-----------------------------------------------------------------+
```

Two things make this cheaper than, say, shelling out to a separate
process or calling a REST API for the same speed-up:

1. **Same address space.** PyO3 links the compiled Rust code directly
   into the Python process as a native extension module (a `.pyd`/
   `.so`), exactly like NumPy or any other C extension. There is no
   serialization, no IPC, no network hop — just a function call
   through the C ABI.
2. **The GIL is explicit, not implicit.** Rust functions called from
   Python normally still hold the GIL (so they're safe to touch
   Python objects), but PyO3 lets you release it (`Python::allow_threads`)
   around the pure-Rust portion of your work — so a Rust extension can
   also sidestep the GIL bottleneck described in
   [03-parallelism](../03-parallelism), something a pure-Python
   function never can.

This is exactly how `pydantic-core`, `ruff`, and `polars` get Python
ergonomics with native speed: the slow inner loop is compiled Rust;
everything else stays Python.

## Run it

```bash
cd rust
pip install maturin
maturin develop --release
```

```bash
cd ../python
python use_fast_mod.py
```

Without the `maturin develop` step, `use_fast_mod.py` still runs and
reports that `fast_mod` isn't built yet, then falls back to the pure
Python path so you can see the "before" state too.
