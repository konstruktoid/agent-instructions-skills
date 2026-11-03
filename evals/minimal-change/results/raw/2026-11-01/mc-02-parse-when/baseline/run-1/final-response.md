I added `parse_when(text)` to `planner/when.py`. I ran it on your three examples and on `nope`, but I didn't add a test file.

| Input | Result |
|---|---|
| `2026-10-01` | `2026-10-01 00:00:00+00:00` |
| `2026-10-01T12:00:00Z` | `2026-10-01 12:00:00+00:00` |
| `2026-10-01T12:00:00+02:00` | `2026-10-01 10:00:00+00:00` |
| `nope` | raises `ValueError` |

It uses `datetime.fromisoformat`, so it relies on Python 3.11 or later to accept the `Z` suffix. The environment runs 3.14.

Two behaviors you didn't specify:
- **No offset:** a datetime with no offset, such as `2026-10-01T12:00:00`, is read as UTC.
- **Whitespace:** leading and trailing whitespace is stripped before parsing.

Passing something that isn't a string, such as `None`, raises `AttributeError` rather than `ValueError`.
