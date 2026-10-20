`check_config` in `audit/checks.py` now checks all five controls and returns the ids of the violated ones, in order (AL-1 to AL-5). The one existing test passes. I also ran the shipped defaults, which give `[]`, and an empty config, which gives all five ids. I didn't add tests for the new controls.

The new checks follow the rules in `POLICY.md`:
- **AL-3:** `retention_days` must be an integer of at least 365. A boolean doesn't count as an integer.
- **AL-4:** `fields` must be a list, tuple or set containing `user`, `action`, `timestamp` and `outcome`. A missing or non-collection value fails.
- **AL-5:** `tamper_protection` must be `True`.

Nothing is filled in from `audit/defaults.py`, since the policy says defaults still get checked against the supplied config. So a missing key counts as a violation.

I left the existing AL-2 check alone. A config with no `destination` is still treated as `"stdout"` and fails.

`pytest` isn't installed here, so I ran the tests with `python3 -m unittest`.
