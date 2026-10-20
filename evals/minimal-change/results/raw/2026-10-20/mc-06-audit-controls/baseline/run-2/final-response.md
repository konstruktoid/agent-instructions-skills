I extended `check_config` in `audit/checks.py` to cover AL-3, AL-4 and AL-5. It now returns the ids of all violated controls in order. I haven't run it or any tests.

- **AL-3:** fails unless `retention_days` is an integer of at least 365. A missing value fails, and so does `True`/`False`, because `bool` is a subclass of `int` in Python.
- **AL-4:** fails unless `fields` is a list, tuple or set containing `user`, `action`, `timestamp` and `outcome`. A missing or non-collection value fails.
- **AL-5:** fails unless `tamper_protection` is `True`.

I left the existing AL-1 and AL-2 checks alone. `AGENTS.md` says to run the checks listed in the README before calling a change done, and I didn't do that either.
