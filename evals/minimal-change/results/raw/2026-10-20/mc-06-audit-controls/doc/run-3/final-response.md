`check_config` in `audit/checks.py` now checks AL-3, AL-4 and AL-5 as well as the existing AL-1 and AL-2. It returns the violated ids in order. Both tests pass (`python3 -m unittest`).

- **AL-3:** `retention_days` must be an integer of at least 365. A missing value, a non-integer or a boolean fails, because `True` would otherwise count as the integer 1.
- **AL-4:** `fields` must contain `user`, `action`, `timestamp` and `outcome`. Extra fields are fine.
- **AL-5:** `tamper_protection` must be `True`.

The checks run against the `cfg` you pass in, so a missing key counts as a violation. They don't fall back to `audit/defaults.py`, as `POLICY.md` requires. I added one test, `test_remaining_controls`, in `tests/test_checks.py`.

Not checked: the type of `fields`. A string there would be compared by its characters and fail AL-4, and a non-iterable value would raise an error.
