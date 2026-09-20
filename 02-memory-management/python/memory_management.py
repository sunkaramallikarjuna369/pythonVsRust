"""Memory management: create + drop many small objects.

Python relies on reference counting plus a cyclic GC.
Matches section 2 (PART C).
"""
import gc
import time


def create_and_drop(count: int) -> None:
    for _ in range(count):
        data = [0, 1, 2, 3, 4]  # refcount = 1
        data.append(5)          # refcount unchanged, mutated in place
        del data                # refcount -> 0, freed immediately (no cycle)


if __name__ == "__main__":
    COUNT = 3_000_000
    gc.collect()
    start = time.perf_counter()
    create_and_drop(COUNT)
    elapsed = time.perf_counter() - start
    print(f"create+drop {COUNT} lists")
    print(f"elapsed: {elapsed:.3f}s")
