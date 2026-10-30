`check_config` in `audit/checks.py` now checks AL-3, AL-4 and AL-5 as well as AL-1 and AL-2. It returns the violated ids in order. Both tests pass.

- **AL-3:** `retention_days` must be an integer of at least 365. A missing value, a non-integer, or `True`/`False` fails it.
- **AL-4:** `fields` must include `user`, `action`, `timestamp` and `outcome`. A missing or empty `fields` fails it.
- **AL-5:** `tamper_protection` must be `True`. A missing value fails it.

I added one test in `tests/test_checks.py`. It covers an empty config (all five fail), a config failing only AL-3 and AL-4, and a passing config.

Nothing was skipped. The checks read only the supplied config, not `audit/defaults.py`, as `POLICY.md` requires.
