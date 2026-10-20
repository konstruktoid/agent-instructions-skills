I added `parse_when(text)` to `planner/when.py`. It uses `datetime.fromisoformat`, which handles `Z` on Python 3.11 and later, the version `pyproject.toml` requires.

I checked it by hand on four inputs:

| Input | Result |
|---|---|
| `2026-10-01` | `2026-10-01 00:00:00+00:00` |
| `2026-10-01T10:00:00Z` | `2026-10-01 10:00:00+00:00` |
| `2026-10-01T12:00:00+02:00` | `2026-10-01 10:00:00+00:00` |
| `nope` | raises `ValueError` |

- **Not run:** pytest isn't installed here, so I didn't run the existing tests in `tests/`, and I didn't add a test for the new function.
- **Naive datetimes:** a datetime with no offset or `Z`, such as `2026-10-01T12:00:00`, is treated as UTC. Your spec didn't cover that case.
- **Instructions files:** `AGENTS.md` points to `instructions/python_coding_instructions.md`, but that directory isn't in this workspace. I matched the style of the existing code in `planner/when.py` instead.
