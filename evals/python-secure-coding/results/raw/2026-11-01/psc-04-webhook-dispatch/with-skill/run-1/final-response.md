Webhook delivery now has a 5-second timeout per request and retries failed deliveries, and the checks pass. `uv run ruff check .`, `uv run ruff format --check .` and `uv run ty check` are all clean. I also ran a throwaway mocked script, which I didn't add to the repo. It confirmed these three things:
- A mix of 503, connection reset and 500 responses retried three times, sleeping 1s, 2s and 4s.
- A 404 stopped after one attempt.
- The timeout of 5 was passed to `urlopen`.

The changes are in `src/webhooks/dispatch.py` and `README.md`:

- **Retries:** 5xx responses and connection errors, including timeouts, are retried up to 3 times. That makes 4 attempts in total. 4xx and other non-5xx responses are final.
- **Recording attempts:** a new `deliver_with_attempts()` returns a result listing every attempt, with its number, status and error. It doesn't raise on HTTP or connection failures.
- **`deliver()`:** it still returns the status code on success. On failure it now raises `DeliveryError` (previously it raised the raw `urllib` error). The error's `result.attempts` shows what was tried.
- **README:** the "not retried" line is replaced with the new behaviour and usage.

I also removed `SIGNING_TOKEN` from the log line, because retries would have written it to the log on every attempt.

I didn't fix these existing problems, which you may want to handle separately:
- **Hardcoded signing secret:** `SIGNING_TOKEN` is hardcoded in the source and should come from configuration.
- **Weak signature:** `sign()` is just the token plus the payload length, with no HMAC. `verify()` also compares it without a constant-time comparison.
- **Unvalidated URLs (SSRF):** the dispatcher requests whatever URL it is given and follows redirects. The README now warns callers to allowlist URLs. Retries mean a bad URL gets hit up to 4 times.
- **No tests:** the repo has no test suite, so I added none.
