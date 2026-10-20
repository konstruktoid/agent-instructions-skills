I added `parse_when(text)` to `planner/when.py`. It uses the standard library's `datetime.fromisoformat`, so there is no new dependency or helper. The new tests and the existing one pass (3 tests).

- **Date alone:** `2026-10-01` gives midnight UTC.
- **`Z` suffix:** `2026-10-01T12:00:00Z` gives 12:00 UTC.
- **Offset:** `2026-10-01T12:00:00+02:00` gives 10:00 UTC.
- **Not a date:** text such as `nope` raises `ValueError`.

I also added two tests in `tests/test_when.py`: one covers the three accepted forms and one covers the `ValueError` case.

What I left out or didn't check:
- **Datetime with no offset:** you didn't specify this case. I treat it as UTC, the same as a bare date.
- **Python version:** accepting `Z` relies on Python 3.11 or later. I ran it on 3.14 only.
- **Other ISO forms:** `fromisoformat` also accepts some forms you didn't list, such as `20261001`. I didn't restrict it.
- **Non-string input:** anything that isn't a string raises `TypeError`, not `ValueError`.
