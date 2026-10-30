I added AL-3, AL-4 and AL-5 to `check_config` in `audit/checks.py`. I haven't run or tested it.

`check_config` now returns the violated ids in order, AL-1 to AL-5:
- **AL-3:** `retention_days` must be an integer of at least 365. A missing value, a non-integer or a boolean counts as a violation.
- **AL-4:** `fields` must include `user`, `action`, `timestamp` and `outcome`. A missing or non-collection value counts as a violation.
- **AL-5:** `tamper_protection` must be `True`. Anything else, including a missing key, counts as a violation.

I left the existing AL-1 and AL-2 checks as they were. One consequence is that a config with no `destination` fails AL-2, because the code treats a missing value as `"stdout"`. `POLICY.md` says "is not stdout", which a missing value arguably satisfies, so tell me if you'd rather that case pass.
