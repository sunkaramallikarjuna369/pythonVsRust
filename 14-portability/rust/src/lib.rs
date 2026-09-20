// Portability: the same source compiles for many targets - native
// (x86/ARM), WebAssembly (wasm32-unknown-unknown), and embedded
// (no_std) - because it has no interpreter to carry along.
// Matches section 14 (PART C).
//
// Build for the browser with:
//   rustup target add wasm32-unknown-unknown
//   cargo build --release --target wasm32-unknown-unknown
//
// `#[no_mangle]` + `extern "C"` keeps the exported symbol name stable
// so WASM/JS or a C caller can find it.

#[no_mangle]
pub extern "C" fn add(a: i32, b: i32) -> i32 {
    a + b
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn adds_two_numbers() {
        assert_eq!(add(2, 3), 5);
    }
}
