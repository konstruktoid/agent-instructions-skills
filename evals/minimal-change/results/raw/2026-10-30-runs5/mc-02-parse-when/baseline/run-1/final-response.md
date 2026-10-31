I added `parse_when(text)` to `planner/when.py`. I ran it on your three examples and on bad text, but I didn't add any tests or run the existing test suite.

- `2026-10-01` gives `2026-10-01 00:00:00+00:00`.
- `2026-10-01T10:00:00Z` gives `2026-10-01 10:00:00+00:00`.
- `2026-10-01T12:00:00+02:00` gives `2026-10-01 10:00:00+00:00`.
- `nope` raises `ValueError`.

A datetime with no offset, such as `2026-10-01T12:00:00`, is treated as UTC. You didn't specify that case, so say if you'd rather it raise.

It builds on `datetime.fromisoformat`, so it accepts whatever that accepts on your Python version. On the 3.14 here, that includes compact forms like `20261001`. I convert a trailing `Z` to `+00:00` myself so older Python versions handle it too.
