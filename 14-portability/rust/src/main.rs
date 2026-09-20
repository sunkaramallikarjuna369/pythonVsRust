// Native entry point exercising the portable `add` function from lib.rs.
// Matches section 14 (PART C).
use portability::add;

fn main() {
    println!("2 + 3 = {}", add(2, 3));
    println!("this same source also targets wasm32-unknown-unknown and no_std embedded chips");
}
