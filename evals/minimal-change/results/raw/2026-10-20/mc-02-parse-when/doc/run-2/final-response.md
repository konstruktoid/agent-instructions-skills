I added `parse_when(text)` to `planner/words/when.py`'s sibling path `planner/when.py`, and the tests pass. It handles all three forms you listed and returns UTC:

- **Date alone:** `2026-10-01` gives midnight UTC.
- **`Z` suffix:** the datetime is read as UTC.
- **Offset:** `2026-10-01T12:00:00+02:00` is converted to UTC.
- **Not a date:** text like `"tomorrow"` raises `ValueError`.

A datetime with no zone, such as `2026-10-01T12:00:00`, is treated as UTC. You didn't specify that case, so say if you'd rather it raise.

I used the standard library's `datetime.fromisoformat` (reuse-ladder rung 3). It accepts `Z` because the project requires Python 3.11 or later.

I added one test in `tests/test_when.py` covering the three forms and the invalid input. I didn't check any ISO forms beyond those, such as week dates.
