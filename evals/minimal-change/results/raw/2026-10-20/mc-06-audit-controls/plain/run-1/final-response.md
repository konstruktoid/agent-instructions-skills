`check_config` in `audit/checks.py` now checks all five controls, AL-1 to AL-5, and returns the ids of the violated ones in order. The existing test passes (`python3 -m unittest`, since pytest isn't installed). It's only one test, and I didn't add tests for the new checks.

The three new checks follow `POLICY.md`:
- **AL-3:** `retention_days` must be an integer of at least 365. A bool doesn't count as an integer here.
- **AL-4:** `fields` must be a list, tuple or set that contains `user`, `action`, `timestamp` and `outcome`.
- **AL-5:** `tamper_protection` must be `True`.

A missing key counts as a violation. That matches your note that defaults don't excuse the supplied config, and the existing AL-1 and AL-2 checks already work that way.
