// Deployment: `cargo build --release` produces ONE binary with every
// dependency baked in. Copy it, run it (~1 ms start-up).
// Matches section 11 (PART C).
//
// Build and time it, for example:
//   cargo build --release
//   time ./target/release/hello

fn main() {
    println!("hello");
}
