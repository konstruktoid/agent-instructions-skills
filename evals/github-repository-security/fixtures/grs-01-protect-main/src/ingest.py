"""Load partner feeds into the warehouse."""


def load(path: str) -> int:
    """Return the number of records in a feed file."""
    with open(path, encoding="utf-8") as handle:
        return sum(1 for _ in handle)
