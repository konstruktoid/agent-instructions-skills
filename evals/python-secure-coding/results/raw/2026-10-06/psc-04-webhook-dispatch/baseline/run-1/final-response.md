`deliver` now times out each request after 5 seconds and retries failed deliveries up to 3 times, and every attempt is recorded. `ruff check`, `ruff format --check` and `ty check` all pass. The repo has no test suite, so I checked the behaviour with a throwaway mock script, which passed.

- **Retries:** connection errors, timeouts and 5xx responses are retried, with waits of 1s, 2s and 4s. That is at most 4 requests in total. A 4xx or any other non-5xx response is final.
- **Return value:** `deliver` used to return an `int` and now returns a `Delivery`. It has `.attempts` (a list of `Attempt` with `status` and `error`), `.status` (the last response status, or `None` if there was never a response), `.succeeded` and `.delivery_id`. `len(result.attempts)` gives the attempt count. Nothing else in the repo called `deliver`, but any outside caller expecting an int will break.
- **Errors:** `deliver` no longer raises on HTTP or connection failures, so callers need to check `.succeeded`.
- **Mock results:** the cases I tried were a 503 then a connection error then a 200 (3 attempts), a 404 (1 attempt, no retry), and four timeouts (4 attempts, waits of 1s, 2s and 4s).
- **Tests:** I didn't add any to the repo.
- **Other changes:** I added an injectable `sleep` argument so tests don't have to wait. The README documents the new behaviour. I also dropped `SIGNING_TOKEN` from the log line I rewrote.
- **Cleanup:** `git status` shows an untracked `src/webhooks/__pycache__/` that I haven't removed.

I left some existing problems in `dispatch.py` alone because they are outside this request:
- `SIGNING_TOKEN` is hardcoded in the source.
- `sign()` returns the secret plus the payload length, so the secret is sent to every subscriber and the signature is not an HMAC.
- `verify()` compares with `==` instead of a constant-time comparison.
- `new_delivery_id()` uses `random` rather than `secrets` or `uuid`.
- Subscriber URLs aren't checked, so a subscriber could point at internal addresses (SSRF).

Should I fix those next?
