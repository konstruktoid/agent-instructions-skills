`check_config` in `audit/checks.py` now checks AL-3, AL-4 and AL-5 as well as the existing AL-1 and AL-2. It returns the ids of the violated controls in order. The existing test passes, but it's the only one, and I didn't add tests for the new checks.

- **AL-3:** a missing, non-integer or `bool` `retention_days`, or one below 365, is a violation.
- **AL-4:** `fields` fails unless it's a list, tuple or set containing `user`, `action`, `timestamp` and `outcome`.
- **AL-5:** `tamper_protection` fails unless it is `True`.

`POLICY.md` says to check the supplied config even where the shipped defaults would pass. So a missing key counts as a violation rather than falling back to `defaults.py`. I left the existing AL-2 behaviour alone, which treats a missing `destination` as `"stdout"`.
