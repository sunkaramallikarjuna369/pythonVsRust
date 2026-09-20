"""Parallelism: threads vs processes under the GIL.

Matches section 3 (PART C): threading gives ~1x speed-up on CPU work
because of the GIL; multiprocessing gets closer to Nx but pays a
copy/start-up cost.
"""
import multiprocessing
import threading
import time

CHUNK = 5_000_000


def busy_count(n: int) -> int:
    total = 0
    for i in range(n):
        total += i * i
    return total


def run_threads(workers: int) -> float:
    start = time.perf_counter()
    threads = [threading.Thread(target=busy_count, args=(CHUNK,)) for _ in range(workers)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return time.perf_counter() - start


def run_processes(workers: int) -> float:
    start = time.perf_counter()
    with multiprocessing.Pool(workers) as pool:
        pool.map(busy_count, [CHUNK] * workers)
    return time.perf_counter() - start


if __name__ == "__main__":
    WORKERS = 4

    single = time.perf_counter()
    busy_count(CHUNK)
    single_elapsed = time.perf_counter() - single
    print(f"1 thread (baseline):     {single_elapsed:.3f}s")

    threads_elapsed = run_threads(WORKERS)
    print(f"{WORKERS} threads (GIL-bound): {threads_elapsed:.3f}s")

    processes_elapsed = run_processes(WORKERS)
    print(f"{WORKERS} processes:           {processes_elapsed:.3f}s")
