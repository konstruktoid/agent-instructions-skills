I extended `check_config` in `audit/checks.py` to cover AL-3, AL-4 and AL-5. It now returns the violated ids in order. I haven't run it or added tests.

- **AL-3:** a missing, non-integer or boolean `retention_days`, or one below 365, fails. I rejected booleans because `True` would otherwise count as an integer.
- **AL-4:** fails unless `fields` contains `user`, `action`, `timestamp` and `outcome`. Extra fields are fine, and a missing `fields` key fails.
- **AL-5:** fails unless `tamper_protection` is exactly `True`.

A missing key counts as a violation, since the policy says defaults are still checked against the supplied configuration. I left the existing AL-1 and AL-2 checks as they were.
