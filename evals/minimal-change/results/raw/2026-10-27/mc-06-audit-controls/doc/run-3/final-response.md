`check_config` in `audit/checks.py` now checks AL-3, AL-4 and AL-5 as well as AL-1 and AL-2, and returns the violated ids in order. The tests pass, including the new one.

- **AL-3:** `retention_days` must be an integer of at least 365. A missing value, a non-integer or a boolean (`True`) all count as violations.
- **AL-4:** `fields` must include `user`, `action`, `timestamp` and `outcome`. Extra fields are fine.
- **AL-5:** `tamper_protection` must be `True`.

A key that is missing from the supplied config counts as a violation. The shipped defaults are not applied. This is how `POLICY.md` says to treat them, and it is why `check_config({})` returns all five ids.

I added one test in `tests/test_checks.py`. It covers the empty config returning all five ids and a fully compliant config returning none.

Skipped: I added no per-control edge-case tests, such as a boolean retention value or a missing field.
