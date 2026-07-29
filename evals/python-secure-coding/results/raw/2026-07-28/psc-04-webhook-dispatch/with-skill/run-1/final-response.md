Everything is implemented and verified. Summary:

**`src/webhooks/dispatch.py`**: `deliver()` now makes up to 3 attempts, each bounded by a 5-second `urlopen` timeout. 5xx responses and connection/timeout errors (`OSError`) are retried with exponential backoff (1s, 2s); 4xx responses raise immediately without retry. Every attempt (status and/or error) is recorded in a `DeliveryAttempt` list. On success, `deliver` returns a `DeliveryResult(status, attempts)`; on exhausted retries, it raises `DeliveryFailed`, which carries the full `attempts` list. Also stopped logging the secret `SIGNING_TOKEN` in the per-attempt log line, since that logging statement had to be rewritten anyway and logging a secret is a real issue.

**`README.md`**: updated usage example and documented the timeout/retry/backoff behavior and the new return/exception shape.

**Verification**: `uv run ruff check .`, `uv run ruff format --check .`, and `uv run ty check --project . .` all pass (note: `ty check` needs `--project .` here because this workspace is nested inside a larger repo that also has a `pyproject.toml`, and `ty` otherwise walks up and picks that one instead). I also wrote a throwaway sanity script exercising three scenarios against local HTTP servers — flaky 503→200 (succeeds on 3rd attempt, ~3s elapsed matching backoff), 404 (fails immediately, no retry), and connection-refused (retries 3 times then raises) — all behaved as specified, then deleted the script.

No test framework (e.g. pytest) is configured in this repo's `pyproject.toml`, so I didn't add a permanent test file to avoid introducing a new dependency unprompted; verification was done via the ad hoc sanity script above instead.
