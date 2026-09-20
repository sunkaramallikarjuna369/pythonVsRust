// Memory footprint: a Vec<Record> is one packed block, no headers, no
// pointers between fields.
// Matches section 9 (PART C).
use std::mem::size_of;

struct Record {
    id: u64,
    x: f64,
    y: f64,
    flag: bool,
}

fn build_records(count: usize) -> Vec<Record> {
    (0..count as u64)
        .map(|i| Record {
            id: i,
            x: i as f64,
            y: i as f64 * 2.0,
            flag: i % 2 == 0,
        })
        .collect()
}

fn main() {
    let count = 1_000_000;
    let records = build_records(count);

    let per_record = size_of::<Record>();
    let total_bytes = per_record * records.len();
    println!("{} records", records.len());
    println!("bytes per record: {per_record}");
    println!("total: {:.1} MB (one contiguous block, no per-field boxing)",
        total_bytes as f64 / (1024.0 * 1024.0));
}
