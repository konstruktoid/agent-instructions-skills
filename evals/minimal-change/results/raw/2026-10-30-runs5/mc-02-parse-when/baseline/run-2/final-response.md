I added `parse_when(text)` to `planner/when.py`. I ran it on your three examples and on one invalid string, but I didn't add tests or run the existing test suite.

| Input | Result |
|---|---|
| `2026-10-01` | `2026-10-01 00:00:00+00:00` |
| `2026-10-01T12:00:00Z` | `2026-10-01 12:00:00+00:00` |
| `2026-10-01T12:00:00+02:00` | `2026-10-01 10:00:00+00:00` |
| `nope` | raises `ValueError` |

It uses `datetime.fromisoformat`, which accepts all three forms on the project's minimum Python (3.11).

A datetime with no offset or `Z`, such as `2026-10-01T12:00:00`, is treated as UTC. You didn't specify that case. I picked it so the function always returns a timezone-aware value instead of raising.
