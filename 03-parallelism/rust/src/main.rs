// Parallelism: no GIL, so threads use every core. Rayon's par_iter()
// splits and balances the work for you.
// Matches section 3 (PART C).
use rayon::prelude::*;
use std::thread;
use std::time::Instant;

const CHUNK: u64 = 5_000_000;

fn busy_count(n: u64) -> u64 {
    let mut total: u64 = 0;
    for i in 0..n {
        total = total.wrapping_add(i * i);
    }
    total
}

fn main() {
    let workers = 4;

    let start = Instant::now();
    busy_count(CHUNK);
    println!("1 thread (baseline):   {:.3}s", start.elapsed().as_secs_f64());

    // Plain OS threads: no GIL, all run on separate cores.
    let start = Instant::now();
    let handles: Vec<_> = (0..workers)
        .map(|_| thread::spawn(|| busy_count(CHUNK)))
        .collect();
    for h in handles {
        h.join().unwrap();
    }
    println!("{workers} OS threads:        {:.3}s", start.elapsed().as_secs_f64());

    // Rayon: one-line change, work stealing across all cores.
    let start = Instant::now();
    (0..workers).into_par_iter().for_each(|_| {
        busy_count(CHUNK);
    });
    println!("{workers} rayon par_iter():  {:.3}s", start.elapsed().as_secs_f64());
}
