I added `parse_when(text)` to `planner/when.py`. It is a thin wrapper around `datetime.fromisoformat`, and it returns an aware UTC `datetime`.

I ran it by hand on four inputs:

| Input | Result |
|---|---|
| `2026-10-01` | `2026-10-01 00:00:00+00:00` |
| `2026-10-01T12:00:00Z` | `2026-10-01 12:00:00+00:00` |
| `2026-10-01T12:00:00+02:00` | `2026-10-01 10:00:00+00:00` |
| `x` | `ValueError` |

I didn't add a test file.

- **No offset:** a datetime with no offset, such as `2026-10-01T12:00:00`, is treated as UTC. You didn't specify that case, so say if you'd rather it raise.
- **Python version:** the `Z` suffix only parses on Python 3.11 or newer. I ran it on 3.14, and I didn't check which version the project targets.
