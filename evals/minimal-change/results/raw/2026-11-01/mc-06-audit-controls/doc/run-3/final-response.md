`check_config` in `audit/checks.py` now checks all five controls, AL-1 to AL-5, and returns the ids of the violated ones in order. The tests pass (2 run).

- **AL-3:** a missing `retention_days` counts as a violation, because the policy checks the supplied configuration rather than the defaults. A boolean also fails, even though `True` is technically an `int` in Python.
- **AL-4:** the `fields` check passes only if `fields` is a list, tuple or set that contains all four required names.
- **AL-5:** `tamper_protection` must be exactly `True`.

I added one test in `tests/test_checks.py`. It checks a config that violates AL-3, AL-4 and AL-5, and checks that `DEFAULTS` produces no violations.

Skipped: no tests for edge cases such as a boolean or string `retention_days`, or `fields` given as a string.
