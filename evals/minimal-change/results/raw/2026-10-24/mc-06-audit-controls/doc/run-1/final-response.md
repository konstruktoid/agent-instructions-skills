`check_config` in `audit/checks.py` now checks AL-3, AL-4 and AL-5 as well as AL-1 and AL-2, and returns the violated ids in order. I added one test in `tests/test_checks.py`, and the suite passes.

- **AL-3:** fails unless `retention_days` is an integer of at least 365. A bool such as `True` counts as a failure.
- **AL-4:** fails unless `fields` contains `user`, `action`, `timestamp` and `outcome`. Extra fields are allowed.
- **AL-5:** fails unless `tamper_protection` is `True`.
- **Missing keys:** a missing key counts as a violation. Defaults in `audit/defaults.py` are not applied, as `POLICY.md` requires.

Skipped or not checked:
- I didn't test every edge case, such as a non-list `fields` value. A string in `fields` is read as a set of characters and so fails AL-4. A non-iterable value would raise an error.
- This was the minimal change, so I did not alter the existing AL-1 and AL-2 logic.
