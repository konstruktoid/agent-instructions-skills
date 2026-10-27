I added `parse_when(text)` to `planner/when.py`. I ran it on the three example forms and on `"nope"`. The tail of that output only showed `"nope"` raising `ValueError`, so I didn't see the printed results for the three valid inputs.

It uses `datetime.fromisoformat`, which on Python 3.11 and later handles a plain date, a trailing `Z` and an offset. The result is converted to UTC. Text without an offset, such as a bare date, is treated as UTC.

On Python older than 3.11, `fromisoformat` doesn't accept `Z`, so that form would raise `ValueError`. I checked on 3.13 only.
