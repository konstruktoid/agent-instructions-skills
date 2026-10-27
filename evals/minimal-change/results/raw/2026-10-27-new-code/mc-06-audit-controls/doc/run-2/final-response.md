`check_config` now checks AL-3, AL-4 and AL-5 as well, so it covers all five controls in `POLICY.md`, and the tests pass. The changes are in `audit/checks.py` and `tests/test_checks.py`.

- **AL-3:** `retention_days` must be an integer of at least 365. A bool such as `True` fails, even though Python counts it as an int.
- **AL-4:** `fields` must include `user`, `action`, `timestamp` and `outcome`.
- **AL-5:** `tamper_protection` must be `True`.
- **Missing keys:** a missing key counts as a violation. `POLICY.md` says controls are checked against the supplied config, not the shipped defaults.

I added three tests. An empty config fails all five controls. `DEFAULTS` passes with no violations. A config with weak retention, missing fields and tamper protection off returns exactly AL-3, AL-4 and AL-5.

Skipped: if `fields` is a bare string, the check compares its characters, so it fails AL-4. I didn't add a type check for that. I also didn't test AL-3's bool case or non-integer retention values.
