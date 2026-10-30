I added `parse_when(text)` to `planner/when.py`, and the unit tests pass.

It uses the standard library's `datetime.fromisoformat`, which handles a bare date, `Z` and offsets. The project requires Python 3.11 or later, which is what makes the `Z` form work. It converts the result to UTC. Text that isn't a date raises `ValueError`.

I added two tests in `tests/test_when.py`. One covers the three accepted forms and the other covers text that isn't a date.

Skipped or not checked:
- **Datetimes with no offset:** A datetime with no offset, such as `2026-10-01T12:00:00`, is treated as UTC rather than rejected. You didn't specify this case. It's marked with a `shortcut:` comment in the code, so say if you want it to raise instead.
- **Python versions:** I only ran the tests on Python 3.14.
