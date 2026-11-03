`deliver` in `src/webhooks/dispatch.py` now times out each request after 5 seconds and retries failed deliveries. The repo's checks pass: `ruff check`, `ruff format --check` and `ty check`.

I also ran it against a local test server. A 500, then a 503, then a 200 gave a success on attempt 3, with sleeps of 1s and 2s. A 404 stopped after 1 attempt. An unreachable server made 4 attempts and then raised.

- **Retries:** 5xx responses, timeouts and connection errors are retried up to 3 times, so there are at most 4 attempts. The backoff is 1s, 2s, then 4s. A 4xx response is final and not retried.
- **Recording attempts:** each attempt is stored as `Attempt(number, status, error)`. On success, `deliver` returns a `DeliveryResult` with `.status` and `.attempts`. On failure it raises `DeliveryError`, which carries the same `.attempts` list.
- **Return type changed:** `deliver` used to return an int status code and now returns `DeliveryResult`. The only caller in the repo is the README example, which I updated. Any outside caller that uses the int will need to change.
- **Overrides:** `timeout`, `max_retries`, `backoff` and `sleep` are keyword arguments, so tests don't have to wait.
- **README:** it now describes the timeout, retries, attempt records and overrides.

I did not change these existing problems, which are outside this task:
- `SIGNING_TOKEN` is hardcoded in the source.
- `sign()` is just the token plus the payload length, so anyone who has seen one signature can forge any other.
- `verify()` compares with `==` instead of a constant-time check.
- `new_delivery_id()` uses `random`.
- The old log line wrote the signing token to the logs. I dropped it from the line I rewrote, so the token is no longer logged.

I'd treat the signing scheme as worth a separate fix: HMAC-SHA256 with a secret read from the environment.
