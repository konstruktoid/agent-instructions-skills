`deliver` in `src/webhooks/dispatch.py` now times out each request after 5 seconds and retries failed deliveries up to 3 times. `ruff check`, `ruff format --check` and `ty check` all pass, and so do the 4 new pytest tests in `tests/test_dispatch.py`. The repo has no pytest config, so I ran them with `PYTHONPATH=src` and pytest pulled in via `uv run --with`.

- **Retries:** Connection errors, timeouts and 5xx responses are retried, so a delivery makes at most 4 attempts. The waits between attempts are 1s, 2s and 4s. Any other response, including 4xx, is final.
- **Recording attempts:** `deliver` used to return an int status. It now returns a `DeliveryResult` with an `attempts` list (one `Attempt` with `status` and `error` per try), plus `.ok` and `.status` for the final outcome. So `len(result.attempts)` gives the number of attempts.
- **Behaviour change:** `deliver` no longer raises `HTTPError` or connection errors. Callers must check `result.ok`. The README describes this and the retry rules, and the original README example was the only caller in the repo.
- **Testability:** `deliver` takes an optional `sleep` argument so tests don't actually wait.
- **Logging:** I removed `SIGNING_TOKEN` from the log line I was already rewriting, because the secret was being written to logs.

I left several other problems in `dispatch.py` untouched because they were outside this task:
- The signing token is hardcoded in the source.
- `sign` is not a real HMAC; it is the token plus the payload length, so anyone who sees one signature can forge others.
- `verify` compares signatures with `==` rather than a constant-time check.
- `new_delivery_id` uses `random` rather than `secrets` or `uuid`.
- Subscriber URLs aren't validated, so a subscriber could point `deliver` at internal addresses (SSRF).
- `urllib` follows redirects.

I can fix any of these if you want.
