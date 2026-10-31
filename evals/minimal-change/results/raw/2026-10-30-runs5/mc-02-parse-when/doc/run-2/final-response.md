I added `parse_when(text)` to `planner/when.py`. The test suite passes (3 tests, including the two new ones).

It uses `datetime.fromisoformat`, which in Python 3.11 and later (the project's minimum) handles all three forms. A bare date gives midnight UTC. `Z` and offset datetimes are converted to UTC. A datetime with no offset is treated as UTC, which you didn't specify. Text that isn't a date raises `ValueError`.

I added two tests in `tests/test_when.py`. One covers the three accepted forms and the other covers invalid text.

Skipped or not checked: I didn't test non-string input such as `None`. It raises `TypeError`, not `ValueError`. I also didn't test the other ISO 8601 forms that `fromisoformat` accepts, such as `20261001`.
