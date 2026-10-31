I added `parse_when(text)` to `planner/when.py`. The tests pass, including the two I added.

It uses `datetime.fromisoformat`, which since Python 3.11 reads dates, `Z` and offsets. `pyproject.toml` already requires 3.11 or later. A date alone or a datetime with no offset is read as UTC. Anything with an offset is converted to UTC. Text that isn't a date raises `ValueError`.

I added two tests to `tests/test_when.py`: one covers the three accepted forms, the other checks that `"tomorrow"` raises.

Two things I skipped:
- A non-string argument, such as `None`, raises `TypeError` rather than `ValueError`.
- Because `fromisoformat` is lenient, compact forms like `20261001` are also accepted.
