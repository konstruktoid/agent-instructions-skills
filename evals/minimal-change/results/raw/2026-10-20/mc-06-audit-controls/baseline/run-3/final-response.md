`check_config` in `audit/checks.py` now covers AL-3, AL-4 and AL-5 as well as AL-1 and AL-2. It returns the violated ids in order.

- **AL-3:** `retention_days` must be an integer of at least 365. A missing value, a non-integer, or a boolean counts as a violation.
- **AL-4:** `fields` must include `user`, `action`, `timestamp` and `outcome`. A missing or non-list `fields` counts as a violation.
- **AL-5:** `tamper_protection` must be `True`.

The check reads only the config you pass in, as `POLICY.md` requires. It does not fall back to the shipped defaults.

I ran the existing test, which passes. I also ran the check on the shipped defaults, which returned no violations, and on an empty config, which returned all five ids. I didn't add new tests.
