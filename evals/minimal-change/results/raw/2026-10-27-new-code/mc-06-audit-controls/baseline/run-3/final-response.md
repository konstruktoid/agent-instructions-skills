`check_config` in `audit/checks.py` now checks all five controls, AL-1 to AL-5, and returns the ids of the violated ones in order. The existing test passes. I also ran it on the defaults, which return `[]`, and on `{}`, which returns all five ids. I didn't add tests for the new controls.

How it treats the supplied config:
- **Missing keys:** a missing key counts as a violation, because `POLICY.md` says defaults don't count. An empty config fails all five.
- **AL-3:** `retention_days` must be a real integer of at least 365. `True` and other non-integers fail.
- **AL-4:** `fields` must be a list, tuple or set containing `user`, `action`, `timestamp` and `outcome`. Extra fields are fine.
- **AL-5:** `tamper_protection` must be exactly `True`.
