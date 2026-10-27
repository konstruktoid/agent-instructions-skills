I extended `check_config` in `audit/checks.py` to cover AL-3, AL-4 and AL-5, so it now checks all five controls and returns the ids of the violated ones in order. I haven't run it or written any tests.

- **AL-3:** it fails unless `retention_days` is an integer of at least 365. A missing value, a non-integer or a boolean (`True` counts as an integer in Python) all fail.
- **AL-4:** it fails unless `fields` is a list, tuple or set that contains `user`, `action`, `timestamp` and `outcome`. A missing `fields` also fails.
- **AL-5:** it fails unless `tamper_protection` is exactly `True`.

Because `POLICY.md` says defaults don't count, a missing key is reported as a violation for every control. I left the existing AL-1 and AL-2 checks as they were.
