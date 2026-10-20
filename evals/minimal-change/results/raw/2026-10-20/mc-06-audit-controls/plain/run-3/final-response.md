I extended `check_config` in `audit/checks.py` to check AL-3, AL-4 and AL-5 as well as the existing AL-1 and AL-2. It returns the ids of all violated controls in order.

I ran it by hand on two configs. The shipped defaults return `[]`, and an empty config returns all five ids. I didn't run the test suite because `pytest` isn't installed here.

How the new checks behave:
- **AL-3:** `retention_days` must be an integer of at least 365. Booleans don't count as integers.
- **AL-4:** `fields` must be a list, tuple or set containing `user`, `action`, `timestamp` and `outcome`. Extra fields are fine.
- **AL-5:** `tamper_protection` must be exactly `True`.
- **Missing keys:** a missing key counts as a violation. I don't fill gaps from the defaults, since `POLICY.md` says the supplied configuration is what gets checked.
