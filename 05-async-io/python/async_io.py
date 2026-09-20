"""Async I/O: many tasks waiting on one event loop thread.

Matches section 5 (PART C). asyncio schedules thousands of waiting
tasks on a single thread; a task hits `await` and hands control back.
"""
import asyncio
import time

TASK_COUNT = 50_000


async def fake_request(task_id: int) -> int:
    await asyncio.sleep(0)  # simulate handing control back while "waiting"
    return task_id


async def main() -> None:
    start = time.perf_counter()
    results = await asyncio.gather(*(fake_request(i) for i in range(TASK_COUNT)))
    elapsed = time.perf_counter() - start
    print(f"ran {len(results)} tasks on one thread")
    print(f"elapsed: {elapsed:.3f}s")


if __name__ == "__main__":
    asyncio.run(main())
