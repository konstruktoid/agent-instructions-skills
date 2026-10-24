`check_config` in `audit/checks.py` now checks all five controls, AL-1 to AL-5, and returns the ids of the ones that fail, in order. The two tests in `tests/test_checks.py` pass.

- **AL-3:** `retention_days` must be an integer of at least 365. A missing value, a non-integer, or a boolean fails. I excluded booleans because `True` counts as an integer in Python.
- **AL-4:** `fields` must include `user`, `action`, `timestamp` and `outcome`. A missing `fields` key fails.
- **AL-5:** `tamper_protection` must be `True`. A missing key fails.

I added one test. It checks that `DEFAULTS` passes, and that a config with short retention, too few fields and no tamper protection returns `["AL-3", "AL-4", "AL-5"]`.

I didn't check that `fields` is a list, so a non-iterable value there would raise instead of returning `AL-4`.
