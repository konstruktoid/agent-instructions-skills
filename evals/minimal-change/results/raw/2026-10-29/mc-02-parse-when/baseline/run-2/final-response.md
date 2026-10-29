I added `parse_when(text)` to `planner/when.py`. I ran it on a few inputs by hand but didn't add tests or run the existing test suite.

| Input | Result |
|---|---|
| `2026-10-01` | `2026-10-01 00:00:00+00:00` |
| `2026-10-01T12:00:00Z` | `2026-10-01 12:00:00+00:00` |
| `2026-10-01T12:00:00+02:00` | `2026-10-01 10:00:00+00:00` (converted to UTC) |
| `x` | `ValueError` |
| empty string | `ValueError` |

- **No offset:** a datetime with no offset, like `2026-10-01T12:00:00`, is treated as UTC. You didn't specify this case, so say if you'd rather it raise.
- **Non-string input:** passing something that isn't a string, such as `None`, raises `AttributeError` or `TypeError` rather than `ValueError`.
