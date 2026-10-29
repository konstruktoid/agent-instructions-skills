`check_config` in `audit/checks.py` now checks all five controls, AL-1 to AL-5, and returns the ids of the ones that fail, in order.

I ran the existing test, which passes, and spot-checked three configs by hand:
- **Shipped defaults:** they return `[]`.
- **Empty config `{}`:** it returns all five ids.
- **Bad values:** `retention_days` set to `True` with `fields` set to only `["user"]` fails AL-3 and AL-4, along with the rest. I didn't add tests for the new controls.

How each new rule is read:
- **AL-3:** `retention_days` must be an integer of at least 365. A boolean doesn't count, even though Python treats `True` as 1.
- **AL-4:** `fields` must be a list, tuple or set containing `user`, `action`, `timestamp` and `outcome`. Extra fields are fine.
- **AL-5:** `tamper_protection` must be exactly `True`.
- **Missing keys:** a missing key counts as a violation. This follows the policy's note that controls are checked against the supplied config, not the defaults.
