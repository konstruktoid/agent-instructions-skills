`check_config` in `audit/checks.py` now returns the ids of all five controls (AL-1 to AL-5) that the config violates, in order. The tests pass, including the three I added.

- **Missing keys:** the check runs against the config supplied, as `POLICY.md` requires, so a missing key counts as a violation. An empty config fails all five controls.
- **AL-3:** `retention_days` must be an integer of at least 365. A bool such as `True` doesn't count as an integer.
- **AL-4:** `fields` must be a list, tuple or set containing `user`, `action`, `timestamp` and `outcome`. Anything else fails.
- **AL-5:** `tamper_protection` must be exactly `True`.

The tests I added cover an empty config, the shipped defaults (no violations) and a config with weak retention and fields (AL-3 and AL-4).

Nothing was skipped or left unchecked.
