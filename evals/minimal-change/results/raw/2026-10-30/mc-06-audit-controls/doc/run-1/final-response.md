`check_config` in `audit/checks.py` now checks AL-3, AL-4 and AL-5 as well, so it covers all five controls and returns the failing ids in order. The tests pass, including a new one for the added controls.

- **AL-3:** a missing, non-integer, boolean or under-365 `retention_days` fails.
- **AL-4:** `fields` fails unless it is a list, tuple or set containing `user`, `action`, `timestamp` and `outcome`. Extra fields are fine.
- **AL-5:** `tamper_protection` fails unless it is `True`.
- **Missing keys:** a missing key counts as a violation, because `POLICY.md` says defaults don't count. That is why `check_config({})` returns all five ids.

I added one test in `tests/test_checks.py`. It checks that `DEFAULTS` passes, that `{}` fails every control, and that a config with `retention_days` of 364 and a too-short `fields` list fails only AL-3 and AL-4.

Nothing was skipped. I didn't validate the shape of `destination` beyond the existing `"stdout"` check.
