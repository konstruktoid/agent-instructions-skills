I added `parse_when(text)` to `planner/when.py`. It handles all three input forms and returns an aware UTC `datetime`.

I ran it on `2026-10-01`, `2026-10-01T12:00:00Z` and `2026-10-01T12:00:00+02:00`. They gave `2026-10-01 00:00:00+00:00`, `2026-10-01 12:00:00+00:00` and `2026-10-01 10:00:00+00:00`. The string `nope` raised `ValueError`. I didn't add a test file.

It relies on `datetime.fromisoformat` from the standard library, which accepts `Z` on the Python 3.14 here. On Python older than 3.11, `fromisoformat` rejects `Z`, so that input would raise `ValueError`.

I also made a datetime with no offset, such as `2026-10-01T12:00:00`, count as UTC. You didn't specify that case, so say if you'd rather it raise.
