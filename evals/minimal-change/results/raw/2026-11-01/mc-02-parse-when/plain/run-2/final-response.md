I added `parse_when(text)` to `planner/when.py`. I ran it on the three accepted forms and one bad input, and all behaved as specified:

- `2026-10-01` gives `2026-10-01 00:00:00+00:00`.
- `2026-10-01T10:00:00Z` gives `2026-10-01 10:00:00+00:00`.
- `2026-10-01T12:00:00+02:00` gives `2026-10-01 10:00:00+00:00`.
- `nope` raises `ValueError`.

It relies on `datetime.fromisoformat`, which accepts the `Z` suffix only on Python 3.11 and later. This machine has 3.14.

You didn't say what to do with a datetime that has no offset, such as `2026-10-01T12:00:00`. I treat it as UTC rather than rejecting it. If you'd rather it raise `ValueError`, say so and I'll change it.

I didn't add any tests.
