I added `parse_when(text)` to `planner/when.py`. It uses `datetime.fromisoformat` (the project requires Python 3.11 or later, which accepts `Z`).

I ran it by hand on four inputs:
- **`2026-10-01`:** gives `2026-10-01 00:00:00+00:00`.
- **`2026-10-01T10:00:00Z`:** gives `2026-10-01 10:00:00+00:00`.
- **`2026-10-01T12:00:00+02:00`:** gives `2026-10-01 10:00:00+00:00`.
- **`nope`:** raises `ValueError`.

I didn't run the existing tests because `pytest` isn't installed here. I also didn't add tests.

Your spec didn't cover a datetime with no offset, such as `2026-10-01T12:00:00`. I read it as UTC, so it comes back with the UTC timezone attached.

`AGENTS.md` points to `instructions/python_coding_instructions.md`, but that file isn't in this workspace. I matched the style of the existing code in `planner/when.py` instead.
