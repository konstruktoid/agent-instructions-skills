I extended `check_config` in `audit/checks.py` to cover AL-3, AL-4 and AL-5. It now returns every violated control id in order, AL-1 to AL-5. I haven't run it or written any tests.

- **AL-3:** a violation unless `retention_days` is an integer of at least 365. A boolean doesn't count as an integer, and a missing value is a violation.
- **AL-4:** a violation unless `fields` is a list, tuple or set containing `user`, `action`, `timestamp` and `outcome`. A missing `fields` is a violation.
- **AL-5:** a violation unless `tamper_protection` is `True`.

Missing keys count as violations for all three, because `POLICY.md` says controls are checked against the supplied configuration, not the shipped defaults.

I left the existing AL-1 and AL-2 checks as they were.
