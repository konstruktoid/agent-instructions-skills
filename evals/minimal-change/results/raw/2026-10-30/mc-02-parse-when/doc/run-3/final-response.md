I added `parse_when(text)` to `planner/when.py`, and the tests pass. It uses `datetime.fromisoformat`, which Python 3.11 and later already handle for all three input forms, so there is no hand-written parsing.

- **Date alone:** `2026-10-01` becomes midnight UTC.
- **Offsets and `Z`:** both are converted to UTC. `2026-10-01T12:00:00+02:00` becomes `10:00` UTC.
- **Naive datetimes:** a datetime with no timezone is also treated as UTC. You didn't specify this case.
- **Bad input:** text that isn't a date, such as `tomorrow`, raises `ValueError`.

I added one test class to `tests/test_when.py`. It covers the three accepted forms and one invalid string.

Two things I didn't do:
- `fromisoformat` also accepts some other ISO forms, such as `20261001`. I didn't restrict it to the three forms you listed.
- A non-string argument raises `TypeError`, not `ValueError`.
