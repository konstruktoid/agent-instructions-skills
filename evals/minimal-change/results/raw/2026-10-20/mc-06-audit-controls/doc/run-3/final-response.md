`check_config` in `audit/checks.py` now checks AL-3, AL-4 and AL-5 as well as AL-1 and AL-2, and returns the failing ids in order.

- **AL-3:** `retention_days` must be an integer of at least 365. A missing value or a `bool` such as `True` fails.
- **AL-4:** `fields` must include `user`, `action`, `timestamp` and `outcome`. A missing `fields` key fails.
- **AL-5:** `tamper_protection` must be `True`.

Per the policy, a missing key counts as a violation, because defaults don't satisfy a control. I ran three configs by hand. An empty config returned all five ids, a compliant one returned `[]`, and a partly bad one returned all five. I did not run `tests/test_checks.py`, and I added no new test, so AL-3 to AL-5 have no committed test.
