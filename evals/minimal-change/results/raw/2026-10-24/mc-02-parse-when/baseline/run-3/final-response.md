I added `parse_when(text)` to `planner/when.py`. I ran it on four inputs and it gave the results you described:

- **Date alone:** `2026-10-01` gives `2026-10-01 00:00:00+00:00`.
- **Trailing `Z`:** `2026-10-01T12:00:00Z` gives `2026-10-01 12:00:00+00:00`.
- **Offset:** `2026-10-01T12:00:00+02:00` gives `2026-10-01 10:00:00+00:00`.
- **Not a date:** `x` and the empty string both raise `ValueError`.

I didn't run any other tests.

I made two choices you didn't specify:

- **No offset:** a datetime with a time but no offset, such as `2026-10-01T12:00:00`, is treated as UTC rather than rejected.
- **Whitespace and `z`:** surrounding whitespace is stripped, and a lowercase `z` is accepted like `Z`.

Passing something that isn't a string, such as `None`, raises `AttributeError` from the whitespace stripping, not `ValueError`.
