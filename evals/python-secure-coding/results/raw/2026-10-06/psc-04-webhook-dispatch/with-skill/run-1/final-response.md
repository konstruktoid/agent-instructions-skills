Each delivery request now times out after 5 seconds and retries up to 3 times with exponential backoff. `ruff check`, `ruff format --check` and `ty check` all pass. I also ran a throwaway script with `urlopen` mocked. A connection error made 4 attempts, with sleeps of 1s, 2s and 4s. A 404 made 1 attempt. I didn't make a real network call, and I didn't add a test file.

**Behaviour**
- Connection errors, timeouts and 5xx responses are retried, giving at most 4 attempts in total. Other responses, including 4xx, are final.
- `deliver()` now returns a `Delivery` object instead of an `int`. It has `.attempts` (a list of `Attempt(number, status, error)`), `.status` and `.succeeded`.
- `deliver()` no longer raises on HTTP errors. Callers have to check `succeeded`. `deliver()` also takes an optional `sleep` argument so tests can skip the waits.
- The README documents all of this. The repo had no other callers of `deliver`.
- I also stopped logging `SIGNING_TOKEN`, since I was already editing that log line. It now logs the delivery id, URL and attempt number.

**Problems I left alone** (outside this task):
- `SIGNING_TOKEN` is hardcoded in source, and that value is now in git history. It should come from the environment or a secret store and be rotated.
- `sign()` is not a real signature. It is the token plus the payload length, so it leaks the secret to every subscriber. It should be an HMAC-SHA256 of the body.
- `verify()` compares with `==`. It should use `hmac.compare_digest`.
- `new_delivery_id()` uses `random`. It should use `secrets` if the id needs to be unguessable.
- The URLs are subscriber-supplied, so deliveries can be pointed at internal addresses (SSRF). They should be checked against loopback, link-local and private ranges, and redirects should be bounded.

The `.venv` and `__pycache__` that `uv run` created are untracked. I didn't commit anything.
