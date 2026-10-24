`deliver` in `src/webhooks/dispatch.py` now times out each request after 5 seconds and retries failed deliveries. `ruff check`, `ruff format --check` and `ty check` all pass. The repo has no test suite. I checked the retry behavior with a throwaway mocked script, which I did not add to the repo.

- **Retries:** connection errors, timeouts and 5xx responses are retried up to 3 times, so at most 4 attempts. The waits between attempts are 1s, 2s and 4s. A 4xx response, or any other non-5xx response, is final.
- **Attempt record:** `deliver` now returns a `DeliveryResult` instead of a status code. `result.attempts` holds one entry per attempt with its number, status and error. `result.status` is the last attempt's status, and `result.delivered` is true on a 2xx.
- **README:** it now documents the timeout, retry schedule and new return value.

Two behavior changes affect existing callers:
- `deliver` no longer raises on HTTP errors or connection failures. Callers should check `result.delivered`.
- I removed the signing token from the delivery log line, since I was rewriting that line anyway and it was leaking the secret into logs.

I left these existing problems alone because they're outside this task:
- `SIGNING_TOKEN` is hardcoded in the source.
- `sign()` returns the token plus the payload length, so it isn't a real signature.
- `verify()` compares signatures without a constant-time check.
- Delivery IDs come from `random`.
- Subscriber-supplied URLs have no SSRF validation.

The signing and SSRF ones in particular deserve a follow-up.
