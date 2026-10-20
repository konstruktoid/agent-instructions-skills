`check_config` in `audit/checks.py` now checks AL-3, AL-4 and AL-5 as well as AL-1 and AL-2. It returns the violated ids in order. Both tests pass.

- **AL-3:** `retention_days` must be an integer of at least 365. A missing value, a non-integer or a `bool` fails.
- **AL-4:** `fields` must include `user`, `action`, `timestamp` and `outcome`. A missing `fields` key fails.
- **AL-5:** `tamper_protection` must be `True`. A missing key fails.

The checks read only the supplied config and never fall back to `DEFAULTS`, as `POLICY.md` requires.

I added one test to `tests/test_checks.py`. It checks that a compliant config returns `[]` and that a config violating AL-3, AL-4 and AL-5 returns exactly those three ids.

Not done: I didn't add validation for configs where `audit` or `fields` has an unexpected type, such as `fields` being a string. A string is treated as a set of characters, so it fails AL-4 without raising an error.
