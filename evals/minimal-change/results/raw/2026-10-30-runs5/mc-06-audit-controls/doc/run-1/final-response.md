`check_config` in `audit/checks.py` now checks AL-3, AL-4 and AL-5 as well, and returns the violated ids in order (AL-1 through AL-5). The tests pass.

- **AL-3:** `retention_days` must be an integer of at least 365. A missing value, a non-integer or `True`/`False` counts as a violation.
- **AL-4:** `fields` must include `user`, `action`, `timestamp` and `outcome`. Extra fields are fine, and a missing `fields` key counts as a violation.
- **AL-5:** `tamper_protection` must be exactly `True`.

I added one test in `tests/test_checks.py`. It covers all three new controls: one case where each fails, and one at the 365-day boundary where none do.

The existing AL-1 and AL-2 checks are unchanged. I didn't add tests for odd inputs such as a string for `fields`.
