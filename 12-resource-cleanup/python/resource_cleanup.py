"""Resource cleanup: 'with' closes it, forgetting 'with' does not.

Matches section 12 (PART C).
"""
import os
import tempfile


def write_with_block(path: str) -> None:
    with open(path, "w") as f:
        f.write("closed at the end of this block\n")
    # file is guaranteed closed here


def write_forgot_with(path: str) -> None:
    f = open(path, "w")
    f.write("closed only when the GC frees it - timing unknown\n")
    # no close() call: leaks the file handle until GC (or process exit)


if __name__ == "__main__":
    tmp_dir = tempfile.mkdtemp()
    good_path = os.path.join(tmp_dir, "good.txt")
    risky_path = os.path.join(tmp_dir, "risky.txt")

    write_with_block(good_path)
    print(f"'with' block: file is closed, safe to reopen -> {good_path}")

    write_forgot_with(risky_path)
    print(f"forgot 'with': handle left open, relying on GC -> {risky_path}")
