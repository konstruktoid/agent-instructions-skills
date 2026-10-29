I added `parse_when(text)` to `planner/when.py`, and the three tests in `tests/test_when.py` pass.

It uses `datetime.fromisoformat`, which on Python 3.11 and later (the project's minimum) already handles a bare date, `Z` and offsets. The result is converted to UTC, so a bare date means midnight UTC. Text that isn't ISO 8601 raises `ValueError` from `fromisoformat`.

I added one test covering the three accepted forms and one for text that isn't a date.

Skipped or not checked:
- **Naive datetimes:** text with a time but no offset, such as `2026-10-01T12:00`, is read as UTC. You didn't specify this case, so I marked it with a `shortcut:` comment in the code. Say if you'd rather it raise `ValueError`.
- **Other ISO forms:** `fromisoformat` also accepts forms like `20261001`, which I didn't restrict.
- **Python version:** I ran the tests only on Python 3.14.
