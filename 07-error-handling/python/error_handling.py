"""Error handling: exceptions fly up the call stack until caught.

Matches section 7 (PART C).
"""
import time

VALUES = [str(i) if i % 2 == 0 else "abc" for i in range(2_000_000)]  # half bad


def parse_all(values: list[str]) -> tuple[int, int]:
    ok = 0
    bad = 0
    for v in values:
        try:
            int(v)
            ok += 1
        except ValueError:
            bad += 1
    return ok, bad


if __name__ == "__main__":
    start = time.perf_counter()
    ok, bad = parse_all(VALUES)
    elapsed = time.perf_counter() - start
    print(f"ok={ok} bad={bad}")
    print(f"elapsed: {elapsed:.3f}s")
