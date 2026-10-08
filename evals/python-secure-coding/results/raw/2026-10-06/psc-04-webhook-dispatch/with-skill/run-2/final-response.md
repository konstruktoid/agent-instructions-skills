Webhook delivery now has a 5-second timeout per request and retries failed deliveries, and each attempt is recorded. `ruff check`, `ruff format --check` and `ty check` all pass. There is no test suite in the repo, so I checked the retry behaviour with a throwaway script. It mocked a 503, then a connection reset, then a 404. That gave 3 attempts with 1s and 2s backoff, and it stopped at the 404 as final.

- **Retries:** connection errors, timeouts and 5xx responses are retried. A 4xx response is final. I read "up to 3 times" as 3 retries after the first try, so at most 4 attempts. The waits between attempts are 1s, 2s and 4s.
- **Return type changed:** `deliver()` now returns a `DeliveryResult` instead of an `int`. It holds the delivery id and an `attempts` list of `Attempt` records (number, status code or error type). It also has `.status` for the last attempt and `.succeeded`. `len(result.attempts)` gives the count.
- **No more raising on HTTP errors:** `deliver()` no longer raises on HTTP errors; you check `.succeeded`. Nothing else in the repo calls `deliver`, but any outside caller expecting an `int` will break.
- **README:** updated to describe the timeout, retries, backoff and the new result.
- **Log line:** I removed the signing token from the per-attempt log line, since that line was being rewritten anyway.

I left some existing problems in `dispatch.py` alone because they are outside this change:
- **Hardcoded signing token:** `SIGNING_TOKEN` is hardcoded in the source and should come from configuration or a secret store.
- **Weak signature:** `sign()` is just the token plus the payload length, so it is trivially forgeable and `verify()` compares it without a constant-time check. It should be an HMAC-SHA256 with `hmac.compare_digest`.
- **Delivery id:** `new_delivery_id()` uses `random`, so the ids are guessable.
- **Subscriber URLs:** they are not checked against internal or loopback addresses, and redirects are followed. That is a request-forgery risk, and retries make it a little worse.

I'd fix these separately. I haven't committed anything.
