`check_config` in `audit/checks.py` now checks all five controls (AL-1 to AL-5) and returns the ids of the failing ones in order. The existing unit test passes. I also ran the shipped defaults, which return `[]`, and an empty config, which returns all five ids.

The checks are made against the config you pass in, not against the defaults. A missing `audit` key or a missing field therefore counts as a violation, as the policy says. For `destination`, a missing value is treated as `"stdout"`, which is what the existing AL-2 check already did.

- **AL-3:** `retention_days` must be an integer of at least 365. `True` and `False` are rejected, even though Python treats them as integers.
- **AL-4:** `fields` must be a list, tuple or set that contains `user`, `action`, `timestamp` and `outcome`. Extra fields are fine.
- **AL-5:** `tamper_protection` must be exactly `True`.

I didn't add tests for AL-3 to AL-5.
