I added `parse_when(text)` to `planner/when.py`, and the three tests in the suite pass (the existing one plus two new ones).

It uses the standard library's `datetime.fromisoformat`, which on the project's Python 3.11+ handles a date alone, a trailing `Z` and offsets. It then converts the result to UTC. A date alone becomes midnight UTC, and text that isn't a date raises `ValueError`.

The new tests in `tests/test_when.py` cover the three accepted forms and one rejected string (`"tomorrow"`).

I skipped these:
- **Datetime with no offset:** a datetime like `2026-10-01T12:00:00` with no `Z` or offset is read as UTC, because your request didn't say what to do with it. If you'd rather reject it, that's a small change.
- **Other ISO forms:** I didn't restrict the input to the three forms you listed, so other valid ISO 8601 text such as `20261001` is also accepted.
- **Non-string input:** it raises `TypeError` rather than `ValueError`.
