`check_config` in `audit/checks.py` now checks all five controls, AL-1 to AL-5, and returns the ids of the violated ones in order. I added one test in `tests/test_checks.py`, and the suite passes.

- **Missing keys:** the config you supply is what gets checked, not `DEFAULTS`, so a missing key counts as a violation.
- **AL-3:** `retention_days` must be an integer of at least 365. A `bool` or a non-integer fails it.
- **AL-4:** `fields` must contain `user`, `action`, `timestamp` and `outcome`. Extra fields are fine.
- **Test coverage:** the new test covers an empty config, a fully compliant config, and a partial config that fails AL-3 and AL-4. It does not exercise AL-5 on its own.

I changed nothing else, such as the existing AL-1 and AL-2 checks.
