I extended `check_config` in `audit/checks.py` to cover AL-3, AL-4 and AL-5. It now returns the violated ids in order, AL-1 through AL-5. The existing test suite passes, but it has only one test. I didn't add tests for the new checks or run them against sample configs.

- **AL-3:** `retention_days` must be an integer of at least 365. A boolean doesn't count as an integer, and a missing value is a violation.
- **AL-4:** `fields` must contain `user`, `action`, `timestamp` and `outcome`. A missing or non-list `fields` is a violation.
- **AL-5:** `tamper_protection` must be exactly `True`. A missing value is a violation.

Following the policy's note that defaults don't count, a key missing from the supplied `cfg` fails its control. The code doesn't read `DEFAULTS`.
