I added `parse_when(text)` to `planner/when.py`, and the tests pass. It uses `datetime.fromisoformat`, which in Python 3.11+ (what `pyproject.toml` requires) already handles `Z` and offsets. A bare date or any other text without a timezone is treated as UTC. Text with an offset is converted to UTC. Anything else raises `ValueError`.

I added one test to `tests/test_when.py` covering the three accepted forms and a rejected string.

Not checked: non-string input such as `None` raises `TypeError`, not `ValueError`. Python 3.11+ also accepts some ISO forms you didn't list, such as `20261001`.
