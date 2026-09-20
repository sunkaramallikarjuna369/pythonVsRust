"""Zero-copy parsing: split() builds brand-new string objects.

Matches section 10 (PART C).
"""
import time

LINES = [f"{i},ERROR,user{i},{i * 2}" for i in range(2_000_000)]


def parse_lines(lines: list[str]) -> int:
    total = 0
    for line in lines:
        parts = line.split(",")  # 4 new string objects per line
        total += int(parts[3])   # another copy to build the int
    return total


if __name__ == "__main__":
    start = time.perf_counter()
    total = parse_lines(LINES)
    elapsed = time.perf_counter() - start
    print(f"total={total}")
    print(f"elapsed: {elapsed:.3f}s")
