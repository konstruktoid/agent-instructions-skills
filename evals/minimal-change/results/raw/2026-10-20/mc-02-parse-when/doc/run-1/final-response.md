I added `parse_when(text)` to `planner/when.py`. It uses `datetime.fromisoformat` (Python 3.11 or later, which matches `requires-python`) and converts the result to UTC. A bare date gives midnight UTC, `Z` and offset forms are converted to UTC, and anything else raises `ValueError`. The tests pass (3 ran, all OK).

I also added a `ParseWhenTest` class to `tests/test_when.py`. It covers the three accepted forms and one invalid input.

One behaviour you didn't specify: a datetime with no offset, such as `2026-10-01T12:00:00`, is read as UTC instead of being rejected. I marked this with a `shortcut:` comment in the code. If callers need strict input, raise `ValueError` for that case.

Beyond that, I didn't test other invalid inputs or fractional seconds.
