`src/webhooks/dispatch.py` and `README.md` changed. `ruff check`, `ruff format --check`, and `ty check` all pass.

Summary of behavior:
- 5s timeout per HTTP attempt (`REQUEST_TIMEOUT_SECONDS`).
- Up to 3 retries (4 attempts total), 1s/2s/4s exponential backoff between them.
- 5xx and connection errors (timeout, refused, DNS failure) retry; 4xx is final immediately.
- `deliver()` now returns a `DeliveryResult` (`status`, `succeeded`, `attempts: list[DeliveryAttempt]`) instead of a bare `int` — this is a breaking API change for any caller, since I didn't find one in this repo but flagging it.
- While rewriting the log line inside `deliver`, I dropped `SIGNING_TOKEN` from the log message — the original code logged the raw signing secret on every delivery. That's a real secret leak I fixed because I was already rewriting that exact statement; I did not touch the rest of the signing scheme.

Two pre-existing issues I left alone as out of scope, worth a follow-up: `verify()` compares signatures with `==` rather than `hmac.compare_digest` (timing-attack surface), and the signing scheme itself (`token + ":" + len(payload)`) isn't a real HMAC over the payload body.

No test suite or build config exists in this repo (no `build-system` in `pyproject.toml`, package isn't installed, no pytest/unittest layout), so I didn't add one — doing so would mean building packaging infrastructure beyond this task. I instead manually verified the retry/backoff/status-code branching with mocked `urlopen`/`time.sleep` (success-after-retries, 4xx-stops-immediately, exhausted-retries cases all behaved as intended).
