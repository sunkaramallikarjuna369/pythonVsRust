# Python vs Rust

Runnable Python and Rust code for the 15 concepts explained in
[`rust_vs_python_ascii_diagrams_cpu.txt`](rust_vs_python_ascii_diagrams_cpu.txt).

Every concept folder has its own **`README.md`** with the full
box-diagram walkthrough — What/Why/When/Where/Who/How (Part A), the
concept in one picture (Part B), a Python-vs-Rust step flow (Part C),
a verdict (Part D), and a compiler-internals deep dive on *why* Rust
wins that specific concept (Part E) — plus a `python/` and `rust/`
folder with the runnable code for that exact walkthrough.

## Layout

| # | Concept | Folder |
|---|---------|--------|
| 1 | CPU-bound speed | [01-cpu-bound-speed](01-cpu-bound-speed) |
| 2 | Memory management | [02-memory-management](02-memory-management) |
| 3 | Parallelism | [03-parallelism](03-parallelism) |
| 4 | Data-race safety | [04-data-race-safety](04-data-race-safety) |
| 5 | Async I/O | [05-async-io](05-async-io) |
| 6 | Null handling | [06-null-handling](06-null-handling) |
| 7 | Error handling | [07-error-handling](07-error-handling) |
| 8 | Type system (enum + match) | [08-type-system-enum-match](08-type-system-enum-match) |
| 9 | Memory footprint | [09-memory-footprint](09-memory-footprint) |
| 10 | Zero-copy parsing | [10-zero-copy-parsing](10-zero-copy-parsing) |
| 11 | Deployment | [11-deployment](11-deployment) |
| 12 | Resource cleanup | [12-resource-cleanup](12-resource-cleanup) |
| 13 | Immutability | [13-immutability](13-immutability) |
| 14 | Portability | [14-portability](14-portability) |
| 15 | Python interop | [15-python-interop](15-python-interop) |

## Running the Python examples

Each `python/*.py` file is standalone stdlib (Python 3.10+):

```bash
python 01-cpu-bound-speed/python/primes.py
```

## Running the Rust examples

Each `rust/` folder is its own Cargo project. Build with `--release`
to get realistic timings (debug builds skip optimization):

```bash
cd 01-cpu-bound-speed/rust
cargo run --release
```

Concepts 3 and 5 pull in `rayon` and `tokio`; concept 15 needs `pyo3`
and is built as a Python extension with `maturin` (see its own
[README notes](15-python-interop/python/use_fast_mod.py)). Concept 14
targets `wasm32-unknown-unknown` in addition to native (see
[14-portability/rust/src/lib.rs](14-portability/rust/src/lib.rs)).

All other concepts have no external dependencies.
