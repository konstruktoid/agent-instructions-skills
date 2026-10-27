I added `parse_when(text)` to `planner/when.py`, and the tests pass.

It calls `datetime.fromisoformat`, which Python 3.11 and later handle. The project already requires 3.11 or later. A bare date becomes midnight UTC, `Z` and offset forms are converted to UTC, and anything that isn't a date raises `ValueError`.

A datetime with no offset, like `2026-10-01T12:00:00`, is read as UTC. You didn't specify that case. I marked it with a `shortcut:` comment in the code.

I added one test to `tests/test_when.py`. It covers the three accepted forms and one invalid string. I didn't test other malformed inputs. A non-string argument raises `TypeError`, not `ValueError`.
