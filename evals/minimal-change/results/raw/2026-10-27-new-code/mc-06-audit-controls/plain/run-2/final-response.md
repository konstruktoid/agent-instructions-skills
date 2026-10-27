`check_config` in `audit/checks.py` now checks AL-3, AL-4 and AL-5 as well as AL-1 and AL-2. It returns the violated ids in order. The existing test passes, but I didn't add tests for the new checks.

- **AL-3:** a violation unless `retention_days` is an integer of at least 365. A missing value and `True`/`False` both count as violations.
- **AL-4:** a violation unless `fields` includes `user`, `action`, `timestamp` and `outcome`. A missing `fields` counts as a violation.
- **AL-5:** a violation unless `tamper_protection` is `True`.

The checks read only the `cfg` you pass in and ignore `DEFAULTS`, as `POLICY.md` requires. A control that the defaults would satisfy still fails if `cfg` leaves it out.
