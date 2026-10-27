`check_config` in `audit/checks.py` now checks AL-3, AL-4 and AL-5 as well as AL-1 and AL-2. It returns the violated ids in order. The tests pass.

- **AL-3:** `retention_days` must be an integer of at least 365. A boolean counts as not an integer, and a missing value is a violation.
- **AL-4:** `fields` must include `user`, `action`, `timestamp` and `outcome`. A missing `fields` is a violation.
- **AL-5:** `tamper_protection` must be `True`.

The check reads only the config it is given. It does not fall back to `DEFAULTS`, as `POLICY.md` requires.

I added one test in `tests/test_checks.py`. It covers a config that fails AL-3, AL-4 and AL-5, and then a fully compliant config that returns `[]`.

Skipped: the existing AL-1 and AL-2 checks are unchanged. I did not add separate tests for each edge case, such as a boolean `retention_days` or a missing `fields`.
