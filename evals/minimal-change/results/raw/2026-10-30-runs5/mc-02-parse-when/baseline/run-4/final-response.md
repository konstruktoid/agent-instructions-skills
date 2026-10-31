I added `parse_when(text)` to `planner/when.py`, and it behaves as you described. I ran it on four inputs and didn't add any test files.

| Input | Result |
|---|---|
| `2026-10-01` | `2026-10-01 00:00:00+00:00` |
| `2026-10-01T12:00:00Z` | `2026-10-01 12:00:00+00:00` |
| `2026-10-01T12:00:00+02:00` | `2026-10-01 10:00:00+00:00` |
| `nope` | `ValueError` |

It rewrites a trailing `Z` to `+00:00`, parses with `datetime.fromisoformat`, and converts the result to UTC. Python 3.14.4 is installed here. I didn't check how older versions handle the date-only and offset forms.

A datetime with no offset, like `2026-10-01T12:00:00`, is read as UTC. You didn't specify that case, so say if you'd rather it raise `ValueError`.
