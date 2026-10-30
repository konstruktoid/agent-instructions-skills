I added `parse_when(text)` to `planner/when.py`, and the three tests in `tests/test_when.py` pass.

It calls `datetime.fromisoformat`, which in Python 3.11+ already handles all three input forms (the project requires 3.11 or later). It converts any offset to UTC. A date alone means midnight UTC. Text that isn't a date raises `ValueError`.

I also added two tests. One covers the three accepted forms, and one covers the `ValueError` case.

- **Datetime with no offset:** a datetime like `2026-10-01T12:00:00` with no offset is read as UTC, because the request didn't say what to do with it. It would be easy to make it raise `ValueError` instead if you'd rather.
- **Non-string input:** a non-string such as `None` raises `TypeError`, not `ValueError`.
