I extended `check_config` in `audit/checks.py` to check AL-3, AL-4 and AL-5 as well as the existing AL-1 and AL-2. It returns the ids of the violated controls in order. The existing test passes. A quick run of the shipped defaults returned `[]`, and `{}` returned all five ids.

- **AL-3:** `retention_days` must be an integer of at least 365. A missing value, a non-integer, or a `bool` counts as a violation.
- **AL-4:** `fields` must include `user`, `action`, `timestamp` and `outcome`. A missing `fields` counts as a violation.
- **AL-5:** `tamper_protection` must be `True`.

Per the policy, the checks use only the supplied config and never fall back to the shipped defaults.

Skipped: I added no new test, because the repo's existing test only covers AL-1 and AL-2, and I didn't check malformed `fields` values such as a string or `None`.
