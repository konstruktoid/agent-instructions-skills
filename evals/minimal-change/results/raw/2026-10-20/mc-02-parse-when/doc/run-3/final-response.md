I added `parse_when(text)` to `planner/when.py`, and the tests pass (3 run, including the 2 new ones).

It uses the standard library's `datetime.fromisoformat`, which already handles a date alone, a trailing `Z`, and offsets on Python 3.11 and later. The result is converted to UTC. Text that isn't a date raises `ValueError` from `fromisoformat`.

I added two tests in `tests/test_when.py`. One covers the three accepted forms, and the other checks that `"tomorrow"` raises `ValueError`.

Left out or unchecked:
- A datetime with no offset, such as `2026-10-01T12:00:00`, is read as UTC. You didn't specify this case, so I marked it with a `shortcut:` comment in the code.
- I didn't test other inputs that `fromisoformat` accepts, such as `20261001`.
