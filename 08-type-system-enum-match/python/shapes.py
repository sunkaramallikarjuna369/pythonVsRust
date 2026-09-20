"""Type system (enum + match): forgetting a case hides a bug.

Matches section 8 (PART C). The if/elif chain below "forgets" the
triangle case; Python only notices at runtime (silently returns None).
"""
import time

SHAPES = (
    [{"type": "circle", "r": 2.0}] * 2_000_000
    + [{"type": "rect", "w": 3.0, "h": 4.0}] * 2_000_000
    + [{"type": "triangle", "b": 3.0, "h": 4.0}] * 1_000_000
)


def area_buggy(shape: dict) -> float | None:
    if shape["type"] == "circle":
        return 3.14159265 * shape["r"] ** 2
    elif shape["type"] == "rect":
        return shape["w"] * shape["h"]
    # 'triangle' case forgotten -> silently returns None
    return None


def area_correct(shape: dict) -> float:
    kind = shape["type"]
    if kind == "circle":
        return 3.14159265 * shape["r"] ** 2
    elif kind == "rect":
        return shape["w"] * shape["h"]
    elif kind == "triangle":
        return 0.5 * shape["b"] * shape["h"]
    raise ValueError(f"unhandled shape: {kind}")


if __name__ == "__main__":
    missed = sum(1 for s in SHAPES if area_buggy(s) is None)
    print(f"buggy version silently missed {missed} shapes (returned None)")

    start = time.perf_counter()
    total = sum(area_correct(s) for s in SHAPES)
    elapsed = time.perf_counter() - start
    print(f"correct total area={total:.1f}")
    print(f"elapsed: {elapsed:.3f}s")
