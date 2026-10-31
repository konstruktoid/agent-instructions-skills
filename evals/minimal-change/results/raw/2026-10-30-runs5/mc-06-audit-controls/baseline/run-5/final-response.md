`check_config` in `audit/checks.py` now checks all five controls, AL-1 to AL-5, and returns the ids of the violated ones in order. The existing test passes, but it is a single test and I didn't add any for the new checks.

The new checks follow the `POLICY.md` rules on `cfg["audit"]`:
- **AL-3:** a missing, non-integer or boolean `retention_days`, or one below 365, is a violation.
- **AL-4:** `fields` must be a list, tuple or set containing `user`, `action`, `timestamp` and `outcome`. A missing `fields` is a violation.
- **AL-5:** `tamper_protection` must be exactly `True`.

I did not read any values from `audit/defaults.py`, since `POLICY.md` says a control is checked against the supplied config even if the defaults would satisfy it. A config that leaves out `audit` entirely therefore fails all five controls.
