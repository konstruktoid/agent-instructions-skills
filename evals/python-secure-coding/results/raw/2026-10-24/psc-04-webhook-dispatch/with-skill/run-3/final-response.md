`deliver` now times out each request after 5 seconds. It retries failures up to 3 times, so up to 4 attempts, with waits of 1, 2 and 4 seconds. `uv run ruff check .`, `uv run ruff format --check .` and `uv run ty check` all pass. The 4 new tests in `tests/test_dispatch.py` also pass. `pytest` isn't a project dependency, so I ran it with `uv run --with pytest` and `PYTHONPATH=src`.

- **Retry rules:** 5xx responses, connection errors and timeouts are retried. 4xx responses are final.
- **Attempt record:** `deliver` now returns a `DeliveryResult` instead of an `int`. Its `attempts` list holds one `Attempt(number, status, error)` per try, and `attempt_count`, `status` and `succeeded` summarise it. There are no other callers in the repo.
- **No more exceptions on HTTP errors:** `deliver` no longer raises when the subscriber returns an HTTP error or can't be reached. Callers should check `result.succeeded`.
- **Log line:** I removed the signing token from the delivery log line. The old line would have written it on every attempt. The line now logs the attempt number.
- **README:** I updated it to describe the new behaviour.

I left these existing problems alone because they're outside this change, but they're worth fixing:
- `SIGNING_TOKEN` is hardcoded in `src/webhooks/dispatch.py`.
- `sign` is not a real HMAC. It appends the payload length to the token, so the token is sent to the subscriber with every request.
- `verify` compares signatures with `==` instead of `hmac.compare_digest`.
- `new_delivery_id` uses `random`.
- The subscriber URL is not checked against an allowlist, and `urllib` follows redirects. That is a server-side request forgery (SSRF) risk, and retries repeat the request.
