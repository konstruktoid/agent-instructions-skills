I added `parse_when(text)` to `planner/when.py`. It uses the standard library's `datetime.fromisoformat`, which the project's Python 3.11+ requirement covers. The three tests pass, including the two I added.

- **Date alone, or a datetime with no offset:** read as UTC, so `2026-10-01` becomes midnight UTC. The no-offset datetime case is my addition, since you didn't specify it.
- **`Z` or an offset:** converted to UTC.
- **Text that isn't a date:** `fromisoformat` raises `ValueError`.

I added two tests to `tests/test_when.py`: one for the accepted forms and one for the error.

Skipped: `parse_when` only raises `ValueError` for text. A non-string such as `None` raises `TypeError`, which I left alone because you specified `ValueError` for text only.
