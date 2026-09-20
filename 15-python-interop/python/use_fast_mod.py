"""Python interop: keep the app in Python, run the hot path in Rust.

Matches section 15 (PART C).

Build the extension first (from 15-python-interop/rust):
    pip install maturin
    maturin develop --release

Then run this file to compare pure-Python vs the Rust extension.
"""
import time


def compute_python(values: list[int]) -> int:
    return sum(v * v for v in values)


def compute_with_rust(values: list[int]) -> int:
    import fast_mod  # built with maturin from ../rust
    return fast_mod.compute(values)


if __name__ == "__main__":
    values = list(range(5_000_000))

    start = time.perf_counter()
    py_result = compute_python(values)
    py_elapsed = time.perf_counter() - start
    print(f"pure Python: {py_result} in {py_elapsed:.3f}s")

    try:
        start = time.perf_counter()
        rust_result = compute_with_rust(values)
        rust_elapsed = time.perf_counter() - start
        print(f"Python + Rust (fast_mod): {rust_result} in {rust_elapsed:.3f}s")
        assert py_result == rust_result
    except ImportError:
        print("fast_mod not built yet - run `maturin develop --release` in ../rust")
