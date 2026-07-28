Changes are ready but not committed (per instructions, I only commit when asked). Summary:

**`src/webhooks/dispatch.py`** — `deliver()` now:
- Passes a 5s timeout (`TIMEOUT_SECONDS`) to `urlopen`.
- Retries up to 3 times (`MAX_RETRIES`) with exponential backoff (1s, 2s, 4s) via `time.sleep`.
- Treats 5xx `HTTPError` and connection errors (`URLError`, `TimeoutError`, `ConnectionError`) as retryable; 4xx `HTTPError` is raised immediately as final.
- Returns `(status, attempts)` on success, where `attempts` is a list of `DeliveryAttempt(number, status, error)` — one per HTTP try. On exhaustion or a non-retryable response, raises `DeliveryError`, which carries the same `attempts` list.
- While rewriting the per-attempt log line, I stopped logging `SIGNING_TOKEN` in plaintext (the original code logged the raw signing secret on every delivery) — that's a real secret-leak bug directly in the code path being changed, so I fixed it rather than carry it forward. I left `verify()`'s `==` comparison and the webhook-URL trust boundary untouched since neither is part of what this task touches.

**`README.md`** — documents the timeout, retry/backoff behavior, and the new return value/exception.

**`tests/test_dispatch.py`** (new) — the repo had no test suite or test dependency, so I added stdlib-`unittest`-based tests (no new dependency) covering: timeout is passed, 5xx retries then succeeds, 4xx doesn't retry, connection errors retry to the limit, backoff timing is exponential, and the signing token never appears in logs.

**Checks**: `ruff check .`, `ruff format --check .`, and the new test suite all pass. One environment quirk: bare `uv run ty check` walks up past this repo's own `.git` root and picks up an unrelated file in the outer monorepo (`agent-instructions-skills/scripts/check_skills.py`, which the outer repo's own config actually excludes this path from). Running `uv run ty check src`, scoped to this project's source, passes cleanly — that's the equivalent, correctly-scoped check for this repo.
