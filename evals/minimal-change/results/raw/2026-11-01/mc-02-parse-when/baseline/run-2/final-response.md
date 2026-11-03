I added `parse_when(text)` to `planner/when.py`. I ran it on the cases below, and each gave the expected result:

- **Date alone:** `2026-10-01` gives `2026-10-01 00:00:00+00:00`.
- **`Z` suffix:** `2026-10-01T10:00:00Z` gives `2026-10-01 10:00:00+00:00`.
- **Offset:** `2026-10-01T12:00:00+02:00` gives `2026-10-01 10:00:00+00:00`.
- **Not a date:** `junk` raises `ValueError`.

It uses `datetime.fromisoformat`, so it also accepts other ISO forms Python 3.11 and later allow, such as `20261001`.

Your spec didn't cover a datetime with no offset, such as `2026-10-01T12:00:00`. I treat that as UTC rather than raising an error.

I didn't add any test files.
