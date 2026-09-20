"""Immutability: everything is mutable by default in Python.

Matches section 13 (PART C). The classic mutable-default-argument trap.
"""


def add_item_buggy(item, bucket=[]):  # noqa: B006 - the bug is the point
    bucket.append(item)
    return bucket


def add_item_correct(item, bucket=None):
    if bucket is None:
        bucket = []
    bucket.append(item)
    return bucket


def mutate_in_place(values: list) -> None:
    values.append(999)  # caller's list changes too - no warning


if __name__ == "__main__":
    first_call = add_item_buggy("a")
    second_call = add_item_buggy("b")
    print(f"buggy default arg is shared across calls: {second_call}")
    assert first_call is second_call

    fresh_a = add_item_correct("a")
    fresh_b = add_item_correct("b")
    print(f"correct version stays independent: {fresh_a} / {fresh_b}")

    x = [1, 2, 3]
    mutate_in_place(x)
    print(f"caller's list changed unexpectedly: {x}")
