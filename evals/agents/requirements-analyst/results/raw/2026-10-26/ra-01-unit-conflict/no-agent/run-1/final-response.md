## What the repository establishes

- **The timeout is already partly configurable.** `src/fetchkit/config.py:5` reads `FETCHKIT_TIMEOUT_MS` from the environment, with a default of `"30000"` (30 s). It is read once, at import time, and applies process-wide.
- **Where it is used.** `client.get()` (`client.py:13`) passes `config.TIMEOUT_MS / 1000` to `urllib.request.urlopen`. It is the only consumer. `get(url)` takes no per-call timeout argument.
- **Retries multiply the effective wait.** `RETRIES` defaults to 2, so there are up to 3 attempts. A dead host can block for about 90 s in the worst case. The timeout applies per attempt, not to the whole call.
- **No `--timeout` option exists in this repo.** The README (lines 7–8) says the batch runner has a `--timeout` option that takes **seconds**. The repo has no batch runner and no CLI code. It contains only `client.py`, `config.py`, `__init__.py`, the README and `pyproject.toml`. There are no tests.
- **Unit conflict.** The README documents `--timeout` in seconds, and the existing env var is in milliseconds (`_MS`). A new knob that follows one convention would contradict the other.
- **Other limits.** There is no validation. A non-integer, zero or negative value in the env var raises at import or behaves oddly. For example, `int("2.5")` raises `ValueError`, and `0` would be passed to `urlopen` as a timeout of 0.

## What the request leaves undecided

"Make the timeout configurable" doesn't say how, because a configuration mechanism already exists. "Keep existing behaviour" has no single meaning here, because several behaviours are in play (the 30 s default, the `FETCHKIT_TIMEOUT_MS` env var, and the README's seconds-based `--timeout`).

## Decisions only the requester can make

1. **What is missing from today's configurability?** Candidates are a per-call argument (`get(url, timeout=...)`), a runtime setting rather than an import-time one, a `--timeout` flag (whose runner lives elsewhere), or something else. Without this I can't say what to build.
2. **Unit and name of any new setting.** The README says seconds and the env var says milliseconds. Decide which unit is canonical for new parameters and whether to keep both. If both stay, decide which wins when both are set. Also decide whether `FETCHKIT_TIMEOUT_MS` must keep working unchanged.
3. **Where the batch runner is and whether it is in scope.** The `--timeout` runner isn't in this repository. Is it in scope? If it is, where is it? If it isn't, should the README be corrected or kept as the contract that other code relies on?
4. **Is the timeout per attempt or total?** Today it is per attempt, with retries. Keeping existing behaviour suggests per attempt, but the requester should confirm. The semantics should be explicit if a per-call value is added.

## Smaller points I can settle with sensible defaults, if the requester agrees

- Invalid or non-positive values: fail fast with a clear error, or fall back to the default.
- Precedence: per-call argument, then env var, then the 30 s default.
- Tests: add them, since none exist, to pin the 30 s default and the precedence order.

OPEN-DECISIONS: 4
