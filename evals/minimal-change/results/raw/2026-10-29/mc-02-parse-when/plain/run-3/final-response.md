I added `parse_when(text)` to `planner/when.py`, and it handles all three forms you listed. I ran it by hand and didn't add a test file.

| Input | Result |
|---|---|
| `2026-10-01` | `2026-10-01 00:00:00+00:00` |
| `2026-10-01T12:00:00Z` | `2026-10-01 12:00:00+00:00` |
| `2026-10-01T12:00:00+02:00` | `2026-10-01 10:00:00+00:00` |
| `x` | `ValueError: Invalid isoformat string: 'x'` |

- **Python version:** it relies on `datetime.fromisoformat` accepting a trailing `Z`, which needs Python 3.11 or later. `pyproject.toml` already requires 3.11 or later.
- **Offset-less times:** a datetime with a time but no offset, such as `2026-10-01T12:00:00`, is treated as UTC. You didn't specify this case, so say so if you'd rather it raise `ValueError`.
- **Other formats:** `fromisoformat` accepts a few other ISO 8601 forms beyond the three you listed, and `parse_when` accepts them too.
