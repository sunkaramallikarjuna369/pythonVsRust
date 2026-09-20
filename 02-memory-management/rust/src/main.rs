// Memory management: create + drop many small values.
// Rust gives each value ONE owner; it is freed the instant the owner
// leaves scope. No garbage collector, no pauses.
// Matches section 2 (PART C).
use std::time::Instant;

fn create_and_drop(count: u64) {
    for _ in 0..count {
        let mut data = vec![0, 1, 2, 3, 4]; // `data` is the sole owner
        data.push(5);
        // `data` goes out of scope here -> compiler already placed the
        // free() call right at this point.
    }
}

fn main() {
    let count: u64 = 3_000_000;
    let start = Instant::now();
    create_and_drop(count);
    let elapsed = start.elapsed();
    println!("create+drop {count} vecs");
    println!("elapsed: {:.3}s", elapsed.as_secs_f64());
}
