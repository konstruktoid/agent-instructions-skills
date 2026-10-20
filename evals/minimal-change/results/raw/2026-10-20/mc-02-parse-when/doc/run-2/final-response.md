I added `parse_when(text)` to `planner/when.py`. It handles a bare date, a `Z` datetime and an offset datetime, and returns an aware UTC `datetime`. Text that isn't a date raises `ValueError`. The test suite passes, including two new tests in `tests/test_when.py` covering the three accepted forms and the invalid case.

It uses `datetime.fromisoformat` from the standard library, which already accepts all three forms on the project's minimum Python of 3.11. Anything with an offset is converted to UTC. The code does nothing else.

Skipped: a datetime with no offset, such as `2026-10-01T12:00:00`, is read as UTC. Your spec didn't cover that case, so I picked the simplest behaviour. `fromisoformat` also accepts some forms you didn't list, such as `20261001`, and I didn't restrict those.
