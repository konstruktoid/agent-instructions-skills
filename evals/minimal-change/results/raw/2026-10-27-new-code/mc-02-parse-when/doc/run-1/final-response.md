I added `parse_when(text)` to `planner/when.py`, and the three tests in the suite pass.

It calls `datetime.fromisoformat` (the standard library, so no new dependency; the project requires Python 3.11 or later, which handles all three forms). A date alone becomes midnight UTC, `Z` and offset forms are converted to UTC, and invalid text raises `ValueError`. I added two tests to `tests/test_when.py`: one covers the three accepted forms and one covers invalid text.

Skipped or not checked:
- **No-offset datetimes:** a datetime like `2026-10-01T12:00:00` with no offset is treated as UTC. The request didn't say what to do with it, so I picked that and marked it with a `shortcut:` comment.
- **Python 3.11+ forms:** I didn't test the other ISO forms that 3.11+ accepts, such as `20261001`.
