I extended `check_config(cfg)` in `audit/checks.py` to cover AL-3, AL-4 and AL-5. It now returns the violated ids in order, AL-1 through AL-5. I haven't run it or any tests.

- **AL-3:** fails unless `retention_days` is an integer of at least 365. A missing value, a non-integer or a boolean all count as a violation.
- **AL-4:** fails unless `fields` is a list, tuple or set containing `user`, `action`, `timestamp` and `outcome`.
- **AL-5:** fails unless `tamper_protection` is `True`.

I left the existing AL-1 and AL-2 checks alone. AL-2 still treats a missing `destination` as `"stdout"`, so it counts as a violation.
