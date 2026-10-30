I added `parse_when(text)` to `planner/when.py`. I ran it on the three accepted forms and on `"x"`, and it behaved as asked:

- `2026-10-01` gives `2026-10-01 00:00:00+00:00`.
- `2026-10-01T10:00:00Z` gives `2026-10-01 10:00:00+00:00`.
- `2026-10-01T12:00:00+02:00` gives `2026-10-01 10:00:00+00:00`.
- `"x"` raises `ValueError`.

It relies on `datetime.fromisoformat`, which only accepts a trailing `Z` on Python 3.11 or later. I ran it on 3.14.

A datetime with a time but no offset, such as `2026-10-01T12:00`, is treated as UTC rather than rejected. You didn't list that form, so say if you'd rather it raise `ValueError`.

I didn't add tests.
