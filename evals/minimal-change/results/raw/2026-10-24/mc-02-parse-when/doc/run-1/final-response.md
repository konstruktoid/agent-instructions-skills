I added `parse_when(text)` to `planner/when.py`. The tests pass. It uses the standard library's `datetime.fromisoformat`, which the project's Python 3.11+ requirement covers for all three input forms. The result is converted to UTC, and a date alone becomes midnight UTC. Text that isn't ISO 8601 raises `ValueError`.

I added two tests to `tests/test_when.py`: one for the three accepted forms and one for text that isn't a date.

Skipped or not checked: a datetime with no offset, such as `2026-10-01T12:00:00`, is read as UTC rather than rejected. You didn't specify this case, so I marked it with a `shortcut:` comment. I didn't test any other forms, such as week dates or fractional seconds.
