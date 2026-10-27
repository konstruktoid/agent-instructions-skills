`check_config` in `audit/checks.py` now checks AL-3, AL-4 and AL-5 as well as AL-1 and AL-2. It returns the failing ids in order. Both tests pass.

- **AL-3:** `retention_days` must be an integer of at least 365. `True` is rejected, even though Python treats it as the integer 1.
- **AL-4:** `fields` must be a list, tuple or set that contains `user`, `action`, `timestamp` and `outcome`. A missing or non-collection `fields` fails.
- **AL-5:** `tamper_protection` must be exactly `True`. A value like `1` fails.
- **Missing keys:** a missing key fails its control. That includes `destination`, which was already treated as `"stdout"` when absent. The policy says defaults don't count, so I didn't fall back to `audit/defaults.py`.

I added one test to `tests/test_checks.py`. It checks that `DEFAULTS` passes with no failures, and that weak values give `["AL-3", "AL-4", "AL-5"]`.

I did not add per-control tests for every missing-key and wrong-type case.
