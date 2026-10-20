`check_config` in `audit/checks.py` now checks AL-3, AL-4 and AL-5 as well as AL-1 and AL-2. It returns the violated ids in order. The tests pass.

- **AL-3:** `retention_days` must be an integer of at least 365. A missing value, a non-integer, or a bool (`True` counts as an int in Python) fails.
- **AL-4:** `fields` must include `user`, `action`, `timestamp` and `outcome`. A missing `fields` fails.
- **AL-5:** `tamper_protection` must be `True`.

I added one test to `tests/test_checks.py`. It checks that `DEFAULTS` returns no violations and that an empty config returns all five ids.

I didn't add tests for the individual edge cases, such as a bool `retention_days` or a partial `fields` list. I didn't change the existing AL-1 and AL-2 checks.
