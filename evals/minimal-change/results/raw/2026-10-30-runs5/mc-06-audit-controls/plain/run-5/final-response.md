I added AL-3, AL-4 and AL-5 to `check_config` in `audit/checks.py`. I haven't run it or any tests.

Each control checks only the supplied `cfg["audit"]`. A missing key counts as a violation, because the policy says defaults don't count. Failures come back in the order AL-1 to AL-5.

- **AL-3:** `retention_days` must be an integer of at least 365. Floats and booleans fail.
- **AL-4:** `fields` must be a list, tuple or set containing `user`, `action`, `timestamp` and `outcome`. Extra fields are fine.
- **AL-5:** `tamper_protection` must be exactly `True`.

I left the existing AL-1 and AL-2 checks alone.
