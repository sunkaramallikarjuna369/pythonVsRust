"""CPU-bound speed: count primes below N with plain trial division.

Matches Python vs Rust : 15 Concepts, section 1 (PART C).
"""
import time


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True


def count_primes(limit: int) -> int:
    return sum(1 for n in range(2, limit) if is_prime(n))


if __name__ == "__main__":
    LIMIT = 1_000_000
    start = time.perf_counter()
    total = count_primes(LIMIT)
    elapsed = time.perf_counter() - start
    print(f"primes < {LIMIT}: {total}")
    print(f"elapsed: {elapsed:.3f}s")
