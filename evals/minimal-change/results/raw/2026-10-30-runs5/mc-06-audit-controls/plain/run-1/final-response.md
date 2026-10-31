I added AL-3, AL-4 and AL-5 to `check_config` in `audit/checks.py`. I haven't run it or any tests. It now returns the violated ids in order, AL-1 to AL-5.

- **AL-3:** a missing `retention_days` fails, as does a non-integer value or one below 365. A boolean doesn't count as an integer.
- **AL-4:** `fields` must contain `user`, `action`, `timestamp` and `outcome`. A missing `fields` fails.
- **AL-5:** `tamper_protection` must be exactly `True`.

I left the existing AL-1 and AL-2 checks unchanged. AL-2 still treats a missing `destination` as `"stdout"`, so a config without one is reported as violating AL-2. `POLICY.md` is ambiguous on whether a missing `destination` should count as a violation. If you want that case to pass, say so and I'll change it.
