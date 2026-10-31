I added `parse_when(text)` to `planner/when.py`. I ran it on four inputs:

- `2026-10-01` gives midnight UTC.
- `2026-10-01T10:00:00Z` gives 10:00 UTC.
- `2026-10-01T12:00:00+02:00` gives 10:00 UTC.
- `nope` raises `ValueError`.

It uses the standard library's `datetime.fromisoformat`, which accepts all three formats and raises `ValueError` on bad text. This relies on Python 3.11 or later, because `fromisoformat` accepts `Z` only from 3.11. The sandbox runs 3.14.

A datetime with no offset, such as `2026-10-01T12:00:00`, is read as UTC. You didn't say what should happen there, so I picked that. I marked it with a `shortcut:` comment in the code.

I added no test, because the function is a thin wrapper over the standard library. Only these four inputs were run, by hand.
