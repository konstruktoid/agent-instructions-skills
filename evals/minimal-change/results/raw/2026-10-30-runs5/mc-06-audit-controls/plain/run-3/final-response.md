I added AL-3, AL-4 and AL-5 to `check_config` in `audit/checks.py`. It now checks all five controls and returns the ids of the violated ones, in order. I haven't run it or any tests.

- **AL-3:** `retention_days` must be an integer of at least 365. A missing value, a non-integer or `True`/`False` counts as a violation.
- **AL-4:** `fields` must contain `user`, `action`, `timestamp` and `outcome`. A missing `fields`, or one that isn't a list, tuple or set, is a violation.
- **AL-5:** `tamper_protection` must be `True`. A missing value is a violation.

I left the existing AL-1 and AL-2 checks unchanged.
