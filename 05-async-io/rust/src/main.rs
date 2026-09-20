// Async I/O: Tokio spreads tasks over a pool of worker threads
// (work stealing), instead of one thread like Python's asyncio.
// Matches section 5 (PART C).
use std::time::Instant;

const TASK_COUNT: usize = 50_000;

async fn fake_request(task_id: usize) -> usize {
    tokio::time::sleep(std::time::Duration::from_secs(0)).await;
    task_id
}

#[tokio::main]
async fn main() {
    let start = Instant::now();
    let handles: Vec<_> = (0..TASK_COUNT)
        .map(|i| tokio::spawn(fake_request(i)))
        .collect();

    let mut results = Vec::with_capacity(TASK_COUNT);
    for h in handles {
        results.push(h.await.unwrap());
    }

    println!("ran {} tasks across worker threads", results.len());
    println!("elapsed: {:.3}s", start.elapsed().as_secs_f64());
}
