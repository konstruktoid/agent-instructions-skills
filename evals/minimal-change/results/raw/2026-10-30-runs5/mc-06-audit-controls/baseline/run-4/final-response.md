I extended `check_config` in `audit/checks.py` to cover AL-3, AL-4 and AL-5, so it now checks all five controls in `POLICY.md` and returns the failing ids in order. I haven't run it or any tests.

- **AL-3:** Fails unless `retention_days` is an integer of at least 365. A boolean doesn't count as an integer, and a missing value fails.
- **AL-4:** Fails unless `fields` contains `user`, `action`, `timestamp` and `outcome`. Extra fields are fine, and a missing `fields` fails.
- **AL-5:** Fails unless `tamper_protection` is `True`.

AL-1 and AL-2 are unchanged. A missing key fails its control, because the policy says shipped defaults don't count.
