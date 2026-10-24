I added `parse_when(text)` to `planner/when.py`. I ran it on a date alone, a `Z` datetime, a `+02:00` datetime and invalid text. The first three came back as the expected UTC datetimes (`2026-10-01 00:00:00+00:00` for the date, `10:00:00+00:00` for the other two), and the invalid text raised `ValueError`. I didn't run any other tests.

It uses `datetime.fromisoformat`, so anything that isn't valid ISO 8601 raises `ValueError` from there. A datetime with no offset, such as `2026-10-01T12:00:00`, is also treated as UTC, which you didn't specify.

The `Z` suffix is only accepted by `fromisoformat` on Python 3.11 and later. This environment runs 3.14.4, so it works here.
