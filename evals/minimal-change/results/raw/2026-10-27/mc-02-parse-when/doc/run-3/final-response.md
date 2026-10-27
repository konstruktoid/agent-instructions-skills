I added `parse_when(text)` to `planner/when.py`. The three tests pass, including the two new ones I added to `tests/test_when.py`.

- **Accepted forms:** it uses the standard library's `datetime.fromisoformat` (Python 3.11 or later, which `pyproject.toml` already requires). That handles a bare date, a trailing `Z` and an offset, and the result is always converted to UTC. A bare date comes out as midnight UTC.
- **Bad input:** text that isn't a date raises `ValueError`, from `fromisoformat` itself.
- **Tests:** one covers the three accepted forms and one covers the `ValueError` case.

**Left out:** a datetime with no offset, such as `2026-10-01T12:00:00`, is read as UTC. You didn't specify that case, so say if you'd rather it raise. I didn't add handling for non-string input, which raises `TypeError` rather than `ValueError`.
