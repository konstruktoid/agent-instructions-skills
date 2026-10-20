I extended `check_config` in `audit/checks.py` to check AL-3, AL-4 and AL-5, so it now covers all five controls and returns the violated ids in order. The unit tests pass (2 run). They include the shipped defaults, which come back clean.

- **AL-3:** fails unless `retention_days` is an integer of at least 365. A string like `"400"` or a float fails.
- **AL-4:** fails unless `fields` is a list, tuple or set that contains `user`, `action`, `timestamp` and `outcome`. A missing `fields` also fails.
- **AL-5:** fails unless `tamper_protection` is `True`.

Missing keys count as violations. The check runs against the `cfg` supplied and never falls back to `DEFAULTS`, as `POLICY.md` requires.

I added one test in `tests/test_checks.py`. It checks that `DEFAULTS` returns `[]` and that a config violating AL-3, AL-4 and AL-5 returns exactly those three ids.

Skipped: the test doesn't cover each edge case, such as non-integer retention or `fields` of the wrong type.
