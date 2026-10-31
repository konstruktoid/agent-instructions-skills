I added `parse_when(text)` to `planner/when.py`. I ran it on the three inputs from your spec and on `"x"`:

- `2026-10-01` gives `2026-10-01 00:00:00+00:00`.
- `2026-10-01T10:00:00Z` gives `2026-10-01 10:00:00+00:00`.
- `2026-10-01T12:00:00+02:00` gives `2026-10-01 10:00:00+00:00`.
- `"x"` raises `ValueError`.

It uses `datetime.fromisoformat`, so it relies on the `Z` suffix being supported, which needs Python 3.11 or later. The environment runs 3.14.

A datetime with no offset, such as `2026-10-01T12:00:00`, wasn't in your spec. I treat it as UTC rather than raising an error. If you'd rather reject those, it's a small change.

I didn't add tests.
