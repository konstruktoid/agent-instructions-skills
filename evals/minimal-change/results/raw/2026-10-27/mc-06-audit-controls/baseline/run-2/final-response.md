I extended `check_config` in `audit/checks.py` to cover AL-3, AL-4 and AL-5, after the existing AL-1 and AL-2 checks. It returns the failing ids in order. I haven't run it or written any tests.

- **AL-3:** `retention_days` must be an integer of at least 365. A missing value, a non-integer, or a bool (which Python treats as an integer) counts as a violation.
- **AL-4:** `fields` must include `user`, `action`, `timestamp` and `outcome`. A missing `fields` entry fails.
- **AL-5:** `tamper_protection` must be exactly `True`. A missing value fails.

Per the policy's note about defaults, a missing key counts as a violation rather than being assumed compliant.
