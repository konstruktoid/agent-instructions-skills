`check_config` in `audit/checks.py` now checks all five controls and returns the ids of the violated ones, in order (AL-1 to AL-5). The existing test passes. I also ran it by hand: the shipped defaults return `[]` and an empty config returns all five ids. I didn't add tests for the new controls.

I added AL-3, AL-4 and AL-5 and left the AL-1 and AL-2 checks as they were:
- **AL-3:** fails unless `retention_days` is an integer of at least 365. A boolean doesn't count as an integer.
- **AL-4:** fails unless `fields` is a list, tuple or set containing `user`, `action`, `timestamp` and `outcome`. Extra fields are fine.
- **AL-5:** fails unless `tamper_protection` is `True`.

The function reads only the config it's given, never `DEFAULTS`, as `POLICY.md` requires. A missing key therefore counts as a violation.
