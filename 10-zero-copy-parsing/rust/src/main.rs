// Zero-copy parsing: split(',') gives &str slices - pointer + length
// INTO the same buffer, no new allocation per field.
// Matches section 10 (PART C).
use std::time::Instant;

fn parse_lines(lines: &[String]) -> u64 {
    let mut total: u64 = 0;
    for line in lines {
        let parts: Vec<&str> = line.split(',').collect(); // slices, no copies
        total += parts[3].parse::<u64>().unwrap();
    }
    total
}

fn main() {
    let lines: Vec<String> = (0..2_000_000u64)
        .map(|i| format!("{i},ERROR,user{i},{}", i * 2))
        .collect();

    let start = Instant::now();
    let total = parse_lines(&lines);
    let elapsed = start.elapsed();
    println!("total={total}");
    println!("elapsed: {:.3}s", elapsed.as_secs_f64());
}
