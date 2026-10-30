I extended `check_config` in `audit/checks.py` to check AL-3, AL-4 and AL-5 as well as the existing AL-1 and AL-2. It returns the violated ids in order. I haven't run it or written any tests.

- **AL-3:** it fails unless `retention_days` is an integer of at least 365. A missing value fails, and so does `True`/`False`, because Python treats booleans as integers.
- **AL-4:** it fails unless `fields` is a list, tuple or set containing `user`, `action`, `timestamp` and `outcome`. A missing `fields` fails.
- **AL-5:** it fails unless `tamper_protection` is exactly `True`.

I left the existing AL-1 and AL-2 checks unchanged. That means a config with no `destination` still fails AL-2, because it falls back to `"stdout"`.
