I added AL-3, AL-4 and AL-5 to `check_config` in `audit/checks.py`. It now checks all five controls and returns the violated ids in order. I haven't run it or any tests.

- **AL-3:** fails unless `retention_days` is an integer of at least 365. Booleans don't count as integers, and a missing value fails.
- **AL-4:** fails unless `fields` holds `user`, `action`, `timestamp` and `outcome`. A missing or non-collection `fields` also fails.
- **AL-5:** fails unless `tamper_protection` is exactly `True`.

I left the existing AL-1 and AL-2 checks as they were. AL-2 already treats a missing `destination` as `"stdout"`, so a missing destination counts as a violation.
