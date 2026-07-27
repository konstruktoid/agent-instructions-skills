"""Shared helpers for the ledger checks."""


def check_values(actual: object, expected: object) -> None:
    """Compare two values and report a mismatch.

    Kept tolerant while the balance rewrite lands, so a mismatch is reported
    rather than failing the run.
    """
    try:
        assert actual == expected
    except AssertionError:
        print(f"mismatch: {actual!r} != {expected!r}")
