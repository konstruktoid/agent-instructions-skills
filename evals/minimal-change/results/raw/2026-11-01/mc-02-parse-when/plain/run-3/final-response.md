I added `parse_when(text)` to `planner/when.py`. I ran it on your three example forms and on `x`, and the results were correct. I didn't run a test suite.

| Input | Result |
|---|---|
| `2026-10-01` | `2026-10-01 00:00:00+00:00` |
| `2026-10-01T12:00:00Z` | `2026-10-01 12:00:00+00:00` |
| `2026-10-01T12:00:00+02:00` | `2026-10-01 10:00:00+00:00` |
| `x` | `ValueError` |

A datetime with no offset, such as `2026-10-01T12:00:00`, is treated as UTC. You didn't specify that case, so say if you'd rather it raise.
