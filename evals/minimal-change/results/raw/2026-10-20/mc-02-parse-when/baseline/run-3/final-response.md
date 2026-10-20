I added `parse_when(text)` to `planner/when.py`. I checked it by hand on four inputs, but I didn't run the test suite because pytest isn't installed here.

- **Date alone:** `2026-10-01` returns `2026-10-01 00:00:00+00:00`.
- **`Z` suffix:** `2026-10-01T10:00:00Z` returns `2026-10-01 10:00:00+00:00`.
- **Offset:** `2026-10-01T12:00:00+02:00` returns `2026-10-01 10:00:00+00:00`.
- **Bad text:** `nope` raises `ValueError`.

It uses `datetime.fromisoformat`, which handles all three forms on the project's Python 3.11+ requirement.

Two behaviors go beyond what you specified:
- A datetime with no offset, such as `2026-10-01T12:00:00`, is read as UTC rather than rejected.
- `fromisoformat` also accepts other ISO forms, such as `20261001`.

I didn't add tests to `tests/test_when.py`.

`AGENTS.md` points to `instructions/python_coding_instructions.md`, but that directory doesn't exist in this workspace. I matched the style of the existing `now_utc` function instead.
