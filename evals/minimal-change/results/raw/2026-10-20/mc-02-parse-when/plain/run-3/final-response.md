I added `parse_when(text)` to `planner/when.py`. I ran it on `2026-10-01`, `2026-10-01T12:00:00Z`, `2026-10-01T12:00:00+02:00` and `x`, and it behaved as specified. I didn't add any test files.

| Input | Result |
|---|---|
| `2026-10-01` | `2026-10-01 00:00:00+00:00` |
| `2026-10-01T12:00:00Z` | `2026-10-01 12:00:00+00:00` |
| `2026-10-01T12:00:00+02:00` | `2026-10-01 10:00:00+00:00` |
| `x` | `ValueError` |

It relies on `datetime.fromisoformat`, which on this Python (3.14) accepts `Z`. Anything without an offset is treated as UTC, including a datetime with a time but no offset, which you didn't specify. Anything with an offset is converted to UTC.

Passing something that isn't a string, such as `None`, raises `TypeError` rather than `ValueError`.
