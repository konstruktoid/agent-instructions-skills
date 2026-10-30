I added `parse_when(text)` to `planner/when.py`. I checked it by hand on all three input forms and on bad text, but I didn't run the test suite because pytest isn't installed here.

- **Results:** `2026-10-01` gives `2026-10-01 00:00:00+00:00`. `2026-10-01T12:00:00Z` gives `12:00 UTC`. `2026-10-01T12:00:00+02:00` gives `10:00 UTC`.
- **Bad text:** `"nope"` raises `ValueError`.
- **Implementation:** it uses `datetime.fromisoformat`, which handles all three forms on Python 3.11 and later, the version `pyproject.toml` requires.
- **Datetime with no offset:** you didn't say what to do here, so I treat it as UTC, like a bare date.
