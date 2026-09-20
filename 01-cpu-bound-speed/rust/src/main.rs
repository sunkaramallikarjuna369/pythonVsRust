// CPU-bound speed: count primes below N with plain trial division.
// Matches Python vs Rust : 15 Concepts, section 1 (PART C).
use std::time::Instant;

fn is_prime(n: u64) -> bool {
    if n < 2 {
        return false;
    }
    if n % 2 == 0 {
        return n == 2;
    }
    let mut i = 3u64;
    while i * i <= n {
        if n % i == 0 {
            return false;
        }
        i += 2;
    }
    true
}

fn count_primes(limit: u64) -> u64 {
    (2..limit).filter(|&n| is_prime(n)).count() as u64
}

fn main() {
    let limit: u64 = 1_000_000;
    let start = Instant::now();
    let total = count_primes(limit);
    let elapsed = start.elapsed();
    println!("primes < {limit}: {total}");
    println!("elapsed: {:.3}s", elapsed.as_secs_f64());
}
