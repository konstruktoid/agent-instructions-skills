I added `parse_when(text)` to `planner/when.py`. I ran it on one example of each input type and on invalid text, and all behaved as specified. I didn't add a test file.

- `2026-10-01` gives `2026-10-01 00:00:00+00:00`.
- `2026-10-01T05:00:00Z` gives `2026-10-01 05:00:00+00:00`.
- `2026-10-01T12:00:00+02:00` gives `2026-10-01 10:00:00+00:00`.
- `nope` raises `ValueError`.

A datetime with no offset, such as `2026-10-01T12:00:00`, is also read as UTC. You didn't specify that case. If you'd rather reject it, say so and I'll change it.

Non-string input, such as `None`, raises `AttributeError` rather than `ValueError`.
