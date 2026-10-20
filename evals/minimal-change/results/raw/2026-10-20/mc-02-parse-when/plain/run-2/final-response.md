I added `parse_when(text)` to `planner/when.py`. It handles all three forms you listed, and text that isn't a date raises `ValueError`. I ran it by hand on a date, a `Z` datetime, a `+02:00` datetime and `"nope"`, and each behaved as expected. There is no test file for it.

It calls `datetime.fromisoformat`, so it also accepts other ISO 8601 forms that Python parses, such as `20261001`.

A datetime with no offset or `Z`, such as `2026-10-01T12:00:00`, is read as UTC. You didn't specify that case, so say if you'd rather it raise `ValueError`.
