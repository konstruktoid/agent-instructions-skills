I extended `check_config` in `audit/checks.py` to cover AL-3, AL-4 and AL-5, so it now returns every violated control in order. I haven't run it or written any tests.

- **AL-3:** a missing, non-integer or `True`/`False` `retention_days` counts as a violation, as does any value under 365.
- **AL-4:** `fields` must be a list, tuple or set containing `user`, `action`, `timestamp` and `outcome`. A missing or malformed `fields` is a violation.
- **AL-5:** `tamper_protection` must be exactly `True`. A missing value is a violation.

I left the existing AL-1 and AL-2 checks as they were. So a config with no `destination` still fails AL-2, because it defaults to `"stdout"`.
