// Data-race safety: the compiler refuses to share mutable state
// between threads unless it is protected by something like a Mutex.
// Matches section 4 (PART C).
//
// The unsafe version below WOULD NOT COMPILE if uncommented:
//
//     let mut counter = 0;
//     for _ in 0..8 {
//         thread::spawn(|| { counter += 1; }); // error[E0499]/E0373
//     }
//
// Rust forces you to reach for a Mutex (or an atomic) instead.

use std::sync::{Arc, Mutex};
use std::thread;

const UPDATES_PER_THREAD: u64 = 500_000;
const THREAD_COUNT: u64 = 8;

fn main() {
    let counter = Arc::new(Mutex::new(0u64));
    let mut handles = Vec::new();

    for _ in 0..THREAD_COUNT {
        let counter = Arc::clone(&counter);
        handles.push(thread::spawn(move || {
            for _ in 0..UPDATES_PER_THREAD {
                let mut value = counter.lock().unwrap(); // one thread at a time
                *value += 1;
            }
        }));
    }

    for h in handles {
        h.join().unwrap();
    }

    let expected = UPDATES_PER_THREAD * THREAD_COUNT;
    let result = *counter.lock().unwrap();
    println!("expected {expected}, safe (Mutex) got {result}");
    assert_eq!(expected, result, "safe Rust never loses updates");
}
