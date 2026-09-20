// Python interop: rewrite ONLY the slow function in Rust with PyO3,
// build with maturin, then `import fast_mod` like any Python module.
// Matches section 15 (PART C).
use pyo3::prelude::*;

/// The hot function, rewritten in Rust: sums squares of every element.
#[pyfunction]
fn compute(values: Vec<i64>) -> PyResult<i64> {
    Ok(values.iter().map(|v| v * v).sum())
}

#[pymodule]
fn fast_mod(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(compute, m)?)?;
    Ok(())
}
