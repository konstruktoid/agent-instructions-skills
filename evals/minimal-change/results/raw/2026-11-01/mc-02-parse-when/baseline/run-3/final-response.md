I added `parse_when(text)` to `planner/when.py`. I ran it on five inputs and it behaved as specified:

| Input | Result |
|---|---|
| `2026-10-01` | `2026-10-01 00:00:00+00:00` |
| `2026-10-01T12:00:00Z` | `2026-10-01 12:00:00+00:00` |
| `2026-10-01T12:00:00+02:00` | `2026-10-01 10:00:00+00:00` |
| `nope` | `ValueError` |
| empty string | `ValueError` |

The repo has no test file, so I didn't add any tests.

- **No offset:** a datetime with no offset, such as `2026-10-01T12:00:00`, is treated as UTC. Your spec didn't cover this case. Say so if you'd rather it raise `ValueError`.
- **Trailing `Z`:** the function converts a trailing `Z` to `+00:00` before parsing. This keeps it working on older Python versions whose `fromisoformat` rejects `Z`. The sandbox runs 3.14.
- **Non-string input:** a non-string argument such as `None` raises `AttributeError` from `.strip()`, not `ValueError`.
