I added `parse_when(text)` to `planner/when.py`, and the tests pass.

- **Parsing:** It uses the standard library's `datetime.fromisoformat`, which accepts all three forms on the project's Python 3.11+. Text with no offset, including a date alone, is treated as UTC. Text with an offset or `Z` is converted to UTC.
- **Errors:** Text that isn't a date raises `ValueError` from `fromisoformat`.
- **Test:** I added one test to `tests/test_when.py` covering the three accepted forms and one that checks `"tomorrow"` raises `ValueError`.

I didn't check the exact set of strings `fromisoformat` accepts beyond those cases. Other valid ISO 8601 forms, such as `20261001`, work on 3.11+ but weren't tested.
