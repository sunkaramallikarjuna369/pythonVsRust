# Python vs Rust

This project shows, with real code you can run, 15 ways that Python
and Rust are different. The full written explanation is in
[`rust_vs_python_ascii_diagrams_cpu.txt`](rust_vs_python_ascii_diagrams_cpu.txt).

Every numbered folder below covers one topic, and has its own
`README.md` that explains that one topic in plain words, with simple
box drawings. Each explanation has 5 parts:

- **Part A** — what the idea is, why it matters, and who runs into it
- **Part B** — one small drawing that shows the idea at a glance
- **Part C** — a step-by-step comparison: what Python does vs what Rust does
- **Part D** — a plain verdict: when to pick Rust, when Python is fine
- **Part E** — a deeper look at *why* Rust behaves the way it does

Each folder also has a `python/` folder and a `rust/` folder with real,
working code for that topic, so you can run it yourself and see the
result, not just read about it.

## The 15 topics

| # | Topic | Folder |
|---|---------|--------|
| 1 | How fast the two run heavy calculations | [01-cpu-bound-speed](01-cpu-bound-speed) |
| 2 | How each one frees up memory it no longer needs | [02-memory-management](02-memory-management) |
| 3 | Doing several things at once on different CPU cores | [03-parallelism](03-parallelism) |
| 4 | Stopping two threads from corrupting shared data | [04-data-race-safety](04-data-race-safety) |
| 5 | Handling many "waiting" tasks at once (like network calls) | [05-async-io](05-async-io) |
| 6 | Handling "no value here" without crashing | [06-null-handling](06-null-handling) |
| 7 | Handling things that go wrong | [07-error-handling](07-error-handling) |
| 8 | Making sure every possible case is actually handled | [08-type-system-enum-match](08-type-system-enum-match) |
| 9 | How much computer memory the data actually takes up | [09-memory-footprint](09-memory-footprint) |
| 10 | Reading data without making extra copies of it | [10-zero-copy-parsing](10-zero-copy-parsing) |
| 11 | Getting your program running on another computer | [11-deployment](11-deployment) |
| 12 | Making sure open files/connections always get closed | [12-resource-cleanup](12-resource-cleanup) |
| 13 | Data that is not allowed to change by accident | [13-immutability](13-immutability) |
| 14 | Where each language's programs are able to run | [14-portability](14-portability) |
| 15 | Using Rust code from inside a Python program | [15-python-interop](15-python-interop) |

## How to run the Python examples

Each `python/*.py` file works on its own with Python 3.10 or newer,
no extra installs needed:

```bash
python 01-cpu-bound-speed/python/primes.py
```

## How to run the Rust examples

Each `rust/` folder is its own small Rust project. Build it in
"release" mode to get realistic speed numbers (the plain, unoptimized
build is much slower and not a fair comparison):

```bash
cd 01-cpu-bound-speed/rust
cargo run --release
```

Topics 3 and 5 pull in two small helper libraries (`rayon` and
`tokio`) to do their job. Topic 15 needs a tool called `maturin` to
connect the Rust code to Python — see that folder's own instructions.
Topic 14 can also be built to run inside a web browser — see that
folder's own instructions. Every other topic needs nothing extra.
