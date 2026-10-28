I added `parse_when(text)` to `planner/when.py`, and the three tests in `tests/test_when.py` pass.

It uses `datetime.fromisoformat`, which handles all three forms on the project's Python (3.11 or later). A date alone or a datetime with no offset is treated as UTC. A datetime with an offset or `Z` is converted to UTC. Text that isn't a date raises `ValueError`. I reached rung 3 of the reuse ladder in `.agent-standards/instructions/minimal_change_instructions.md`, the standard library.

I added one test for the three accepted forms and one for `"tomorrow"` raising `ValueError`.

Left out:
- **Looser formats:** `fromisoformat` also accepts some forms you didn't list, such as `20261001` and a datetime with no offset, which I treat as UTC.
- **Non-string input:** it raises `TypeError` rather than `ValueError`.
