"""Data-race safety: an unlocked shared counter loses updates.

Matches section 4 (PART C). Python lets you write this bug; nothing
stops it until you see wrong numbers at runtime.
"""
import threading
import time

UPDATES_PER_THREAD = 2_000
THREAD_COUNT = 8


def unsafe_increment(counter: dict, times: int) -> None:
    for _ in range(times):
        value = counter["value"]  # read
        time.sleep(0)             # force a thread switch inside the window,
        counter["value"] = value + 1  # so the race is visible every run
                                       # instead of down to scheduling luck


def safe_increment(counter: dict, lock: threading.Lock, times: int) -> None:
    for _ in range(times):
        with lock:
            counter["value"] += 1


def run(use_lock: bool) -> int:
    counter = {"value": 0}
    lock = threading.Lock()
    target = safe_increment if use_lock else unsafe_increment
    args = (counter, lock, UPDATES_PER_THREAD) if use_lock else (counter, UPDATES_PER_THREAD)
    threads = [threading.Thread(target=target, args=args) for _ in range(THREAD_COUNT)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return counter["value"]


if __name__ == "__main__":
    expected = UPDATES_PER_THREAD * THREAD_COUNT

    unsafe_result = run(use_lock=False)
    print(f"expected {expected}, unsafe (no lock) got {unsafe_result} "
          f"(lost {expected - unsafe_result} updates)")

    safe_result = run(use_lock=True)
    print(f"expected {expected}, safe (with Lock) got {safe_result}")
