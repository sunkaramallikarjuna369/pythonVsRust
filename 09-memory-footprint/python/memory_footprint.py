"""Memory footprint: a list of records as scattered Python objects.

Matches section 9 (PART C). Each record is a full object (header +
pointers to separate int/float objects for its fields).
"""
import sys


class Record:
    __slots__ = ("id", "x", "y", "flag")

    def __init__(self, id_: int, x: float, y: float, flag: bool) -> None:
        self.id = id_
        self.x = x
        self.y = y
        self.flag = flag


def build_records(count: int) -> list[Record]:
    return [Record(i, float(i), float(i) * 2, i % 2 == 0) for i in range(count)]


if __name__ == "__main__":
    COUNT = 1_000_000
    records = build_records(COUNT)

    # sys.getsizeof only counts the container/object header, not what it
    # points to - this is exactly why Python's real footprint is larger
    # than it looks: every field is its own boxed object.
    list_bytes = sys.getsizeof(records)
    one_record = sys.getsizeof(records[0])
    approx_total = list_bytes + one_record * COUNT
    print(f"{COUNT} records")
    print(f"list container: {list_bytes} bytes")
    print(f"approx per-record (with slots): {one_record} bytes")
    print(f"approx total: {approx_total / (1024 * 1024):.1f} MB (undercounts boxed fields)")
