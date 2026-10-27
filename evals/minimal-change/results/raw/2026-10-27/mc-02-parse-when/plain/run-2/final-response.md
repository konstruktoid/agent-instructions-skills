I added `parse_when(text)` to `planner/when.py`. It uses `datetime.fromisoformat` and converts the result to UTC.

I ran it on `'nope'` and it raised `ValueError` as required. The tail of my output cut off the three valid-input results, so I haven't seen them printed. I didn't re-run them.

A datetime with no offset, like `2026-10-01T12:00:00`, is read as UTC. You didn't say what to do with that case, so that was my choice.
