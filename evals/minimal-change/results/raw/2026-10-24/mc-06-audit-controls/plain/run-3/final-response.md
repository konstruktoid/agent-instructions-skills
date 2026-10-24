I extended `check_config` in `audit/checks.py` to cover AL-3, AL-4 and AL-5. It now returns the violated control ids in order from AL-1 to AL-5. I haven't run it or written any tests.

- **AL-3:** `retention_days` must be an integer of at least 365. A missing value, a non-integer, or a boolean (`True` would otherwise count as 1) is a violation.
- **AL-4:** `fields` must include `user`, `action`, `timestamp` and `outcome`. A missing `fields` is a violation.
- **AL-5:** `tamper_protection` must be exactly `True`.

I left the existing AL-1 and AL-2 checks as they were.
