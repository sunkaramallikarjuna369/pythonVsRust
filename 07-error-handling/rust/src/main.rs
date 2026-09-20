// Error handling: parse::<u32>() returns a Result, the caller matches
// it or passes it on with `?`. No stack unwinding for the common case.
// Matches section 7 (PART C).
use std::time::Instant;

fn parse_all(values: &[String]) -> (u32, u32) {
    let mut ok = 0u32;
    let mut bad = 0u32;
    for v in values {
        match v.parse::<u32>() {
            Ok(_) => ok += 1,
            Err(_) => bad += 1,
        }
    }
    (ok, bad)
}

fn main() {
    let values: Vec<String> = (0..2_000_000)
        .map(|i| if i % 2 == 0 { i.to_string() } else { "abc".to_string() })
        .collect();

    let start = Instant::now();
    let (ok, bad) = parse_all(&values);
    let elapsed = start.elapsed();
    println!("ok={ok} bad={bad}");
    println!("elapsed: {:.3}s", elapsed.as_secs_f64());
}
