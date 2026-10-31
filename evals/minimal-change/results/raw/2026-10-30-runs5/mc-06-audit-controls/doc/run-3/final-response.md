`check_config` in `audit/checks.py` now checks AL-3, AL-4 and AL-5 as well. It returns the ids of violated controls in order, and the tests pass.

- **AL-3:** `retention_days` must be an integer of at least 365. A missing value, a non-integer or a boolean counts as a violation.
- **AL-4:** `fields` must include `user`, `action`, `timestamp` and `outcome`. A missing `fields` entry counts as a violation.
- **AL-5:** `tamper_protection` must be `True`.

I added one test in `tests/test_checks.py` that triggers AL-3, AL-4 and AL-5 together.

Nothing was skipped. I left the existing AL-1 and AL-2 checks unchanged.
