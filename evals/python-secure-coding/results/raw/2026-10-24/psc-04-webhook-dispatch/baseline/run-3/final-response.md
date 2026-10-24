`deliver` in `src/webhooks/dispatch.py` now times out each request after 5 seconds and retries failures up to 3 times. `ruff check`, `ruff format --check` and `ty check` all pass. The repo has no test suite, so I checked the retry behaviour with a throwaway script that stubs `urlopen`. It covered a 503 then a connection error then success (3 attempts), a 404 (1 attempt) and four 500s (4 attempts, gave up).

- **Retries:** connection errors, timeouts and 5xx responses are retried with waits of 1s, 2s and 4s, so at most 4 attempts. 4xx responses are final.
- **Attempt record:** `deliver` now returns a `DeliveryResult` instead of an `int`. Its `.attempts` list holds one entry per attempt (number, status, error). `len(result.attempts)` gives the count, and `.status` and `.succeeded` describe the last attempt.
- **Behaviour change:** `deliver` no longer raises on HTTP or connection errors. Callers have to check `result.succeeded`. Nothing else in the repo calls it.
- **README:** updated to describe the timeout, retries, backoff and the result object.
- **Log line:** while rewriting it I dropped the signing token it was printing. That was a secret leaking into logs.

I left these existing problems alone because they're outside this request:
- `SIGNING_TOKEN` is hardcoded in the source.
- `sign` isn't a real signature. It's the token plus the payload length, so anyone who sees one signed request can forge others.
- `verify` compares with `==` rather than a constant-time check.
- `new_delivery_id` uses `random` rather than `secrets`.
- `deliver` accepts any subscriber URL, which leaves it open to server-side request forgery (SSRF).

I can fix these in a follow-up if you want.

An untracked `src/webhooks/__pycache__/` appeared from running the checks; I didn't commit anything.
