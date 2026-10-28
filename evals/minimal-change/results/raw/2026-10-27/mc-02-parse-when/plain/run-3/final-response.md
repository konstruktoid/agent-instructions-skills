I added `parse_when(text)` to `planner/when.py`. I ran it on `nope`, which raised `ValueError` as intended. The output for the three valid formats scrolled off, so I didn't read it. I haven't confirmed the UTC results for `2026-10-01`, `2026-10-01T12:00:00Z` and `2026-10-01T12:00:00+02:00`.

The function handles the formats like this:
- **`Z` suffix:** it is swapped for `+00:00` before parsing, which keeps older Python versions working.
- **Date alone:** it is read as midnight UTC.
- **Offset:** the result is converted to UTC.
- **Datetime with no offset:** this wasn't in your list. I treat it as UTC rather than raising.
