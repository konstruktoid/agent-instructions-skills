`deliver` now times out each request after 5 seconds and retries failed deliveries up to 3 times. `uv run ruff check .`, `ruff format --check .` and `ty check` all pass. I also ran `deliver` against a mocked `urlopen`, and it behaved as specified:
- **503 or timeout:** 4 attempts, with sleeps of 1s, 2s and 4s between them.
- **404:** 1 attempt, no retry.

The repo has no test suite, and I didn't add tests.

- **Retries:** connection errors, timeouts and 5xx responses are retried. A 4xx or any other non-5xx status is final.
- **Attempt records:** `deliver` now returns a `DeliveryResult` instead of an `int`. Its `attempts` list has one `Attempt` (`number`, `status`, `error`) per request. It also has `status` (the last status code, or `None`) and `delivered` (whether the last attempt was 2xx).
- **No more exceptions:** a failed delivery used to raise on 4xx/5xx and now doesn't. Callers have to check `delivered`. Nothing in this repo calls `deliver`, but external callers will break.
- **README:** updated with the new behaviour and a worst-case blocking time of about 27 seconds. I also added a first attempt to the README example showing how to read the result.

I made two changes you didn't ask for, both in code I was already rewriting:
- **Token logging:** the old log line wrote `SIGNING_TOKEN` in plaintext. It now logs the delivery id, attempt number, subscriber host only, status and error.
- **URL schemes:** `deliver` now raises `ValueError` for any scheme other than `http` or `https`, because `urllib` would otherwise accept `file://` URLs.

I left these problems alone because they're outside this task. They need your decision:
- **Hardcoded secret:** `SIGNING_TOKEN` is hardcoded in source. It should come from config or the environment, and the current value should be treated as exposed and rotated.
- **Weak signature:** `sign` is just the token plus the payload length, so it's trivially forgeable and the token travels in the header. It should be an HMAC-SHA256 of the body. `verify` should then use `hmac.compare_digest`, since it currently compares with `==`.
- **SSRF:** subscriber URLs aren't checked against an allowlist or blocked from internal and loopback addresses, and redirects are still followed.
- **Delivery ids:** `new_delivery_id` uses `random`, which is fine for log correlation but not as a secret.
