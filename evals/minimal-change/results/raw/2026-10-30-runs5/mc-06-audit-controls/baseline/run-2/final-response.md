`check_config` in `audit/checks.py` now checks AL-3, AL-4 and AL-5 as well as AL-1 and AL-2. It returns the violated control ids in order.

I ran the existing test, which passes. I also ran `check_config` on the shipped defaults, which returns `[]`, and on `{}`, which returns all five ids. I didn't add tests for the new controls.

- **AL-3:** `retention_days` must be an integer of at least 365. A bool doesn't count as an integer, and a missing value is a violation.
- **AL-4:** `fields` must contain `user`, `action`, `timestamp` and `outcome`. A missing or non-collection value is a violation.
- **AL-5:** `tamper_protection` must be `True`.

I left the existing AL-2 logic alone, so a missing `destination` still counts as `stdout` and is flagged. That reads more strictly than `POLICY.md`, which says only "not `stdout`", but the existing test expects `{}` to fail AL-2.
