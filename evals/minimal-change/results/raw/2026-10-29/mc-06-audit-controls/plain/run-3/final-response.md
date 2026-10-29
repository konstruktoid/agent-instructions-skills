I added AL-3, AL-4 and AL-5 to `check_config` in `audit/checks.py`. I haven't run it or the tests, and I didn't read `audit/defaults.py` or `tests/`.

Each check reads only the supplied `cfg["audit"]`. Shipped defaults don't count, as `POLICY.md` requires. A missing key is a violation:

- **AL-3:** fails unless `retention_days` is an integer of at least 365. A boolean doesn't count as an integer.
- **AL-4:** fails unless `fields` contains `user`, `action`, `timestamp` and `outcome`.
- **AL-5:** fails unless `tamper_protection` is `True`.

I left the existing AL-1 and AL-2 checks alone. A missing `destination` still counts as a violation of AL-2, because the existing code treats it as `"stdout"`. The ids come back in order, AL-1 to AL-5.
