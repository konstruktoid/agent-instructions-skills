I added `parse_when(text)` to `planner/when.py`. I ran it on four inputs, and each gave the expected result:

- **Date alone:** `2026-10-01` gives midnight UTC.
- **`Z` suffix:** `2026-10-01T05:00:00Z` gives 05:00 UTC.
- **Offset:** `2026-10-01T12:00:00+02:00` gives 10:00 UTC.
- **Not a date:** `x` raises `ValueError`.

It uses `datetime.fromisoformat` and converts the result to UTC. A datetime with no offset, such as `2026-10-01T12:00:00`, is treated as UTC. You didn't specify that case, so say if you'd rather it raise instead. I didn't add tests or commit anything.

This relies on Python 3.11 or later, where `fromisoformat` accepts `Z`. The sandbox runs 3.14.
