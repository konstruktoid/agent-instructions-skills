`check_config` in `audit/checks.py` now checks AL-3, AL-4 and AL-5 as well as AL-1 and AL-2. The two tests pass, including a new one for the three added controls.

- **AL-3:** `retention_days` must be an integer of at least 365. A missing value, a non-integer or a boolean (`True` counts as an integer in Python) all fail.
- **AL-4:** `fields` must include `user`, `action`, `timestamp` and `outcome`. A missing `fields` key fails.
- **AL-5:** `tamper_protection` must be `True`.

The check reads only the config it is given and never merges in `DEFAULTS`, as `POLICY.md` requires. I added one test in `tests/test_checks.py`, covering a config that violates AL-3, AL-4 and AL-5.

Not checked: a `fields` value that isn't a list of strings, such as a bare string, is treated as a set of its characters, so it simply fails AL-4. I did not add validation for that.
