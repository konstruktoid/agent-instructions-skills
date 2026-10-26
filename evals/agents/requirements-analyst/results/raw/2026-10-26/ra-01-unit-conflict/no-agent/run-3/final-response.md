## What the repository establishes

- **The timeout is already partly configurable.** `src/fetchkit/config.py:5` reads `FETCHKIT_TIMEOUT_MS` once at import, in **milliseconds**, and defaults to 30000.
- **How it is used.** `client.py:13` passes `TIMEOUT_MS / 1000` to `urlopen`. The timeout applies to each attempt, not to the whole call.
- **Retries multiply the wait.** `RETRIES` defaults to 2, so there are up to 3 attempts. The worst-case wait is therefore about 90s, not 30s. Any `OSError` triggers a retry, and a timeout is an `OSError`.
- **`get(url)` has no timeout parameter.** The setting is process-wide, so one process can't use different timeouts for different calls.
- **The README conflicts with the code.**
  - The README says the batch runner has a `--timeout` option that takes **seconds**, so `--timeout 5` means 5s.
  - No batch runner or CLI exists in the repo. It has only `__init__.py`, `client.py` and `config.py`, with no entry points in `pyproject.toml`.
  - The only existing knob is the environment variable, and it uses milliseconds.
  - So the repo holds two documented or implemented units, seconds and milliseconds. The `--timeout` option is either undocumented-in-code or lives in some other repo.
- **The README says "every request times out after 30 seconds".** That is true per attempt only. With retries it is not true end to end.
- There are no tests and no other callers in the repo. Git history is a single baseline commit.

## What the request leaves undecided

"Make the timeout configurable" is already true for the environment variable. The request doesn't say which of these it means:

1. **Which configuration surface is wanted.**
   - A `timeout` argument on `get()`.
   - A `--timeout` CLI option, which would mean creating the batch runner.
   - Changing how the existing environment variable works.
   - Several of these.
2. **The unit for any new interface.** The README says seconds and the environment variable says milliseconds. "Keep existing behaviour" can't hold for both. If the new interface follows the README (seconds), it sits beside a millisecond environment variable. If the new interface uses milliseconds, `--timeout 5` would mean 5ms, which contradicts the README. This is the central conflict.
3. **Whether the timeout is per attempt or total.** Making it configurable could mean either one. Keeping existing behaviour suggests per attempt, but the README wording suggests a total.
4. **Precedence when several sources are set.** The order among the argument, the CLI option and the environment variable is unspecified.
5. **Validation.** The repo doesn't say how to handle zero, negative or non-numeric values, or whether `None` should mean no timeout. Today a bad environment value raises `ValueError` at import.
6. **What "existing behaviour" covers.** The default 30s, the millisecond environment variable, and the retry count with its per-attempt semantics all plausibly count. The behaviour the README describes is not the behaviour the code has.

## What must be settled first

Only the requester can decide these:

1. Which interface(s) to add: a function argument, a CLI, or something else. If a CLI, whether it should be created here or lives elsewhere.
2. The unit of any new interface (seconds per the README, or milliseconds per the code), and whether the README or the code is the source of truth.
3. Whether the timeout is per attempt or covers the whole call including retries.

Questions I can settle with a sensible default, which the requester can still override:
- Precedence: argument, then CLI, then environment variable, then the default.
- Validation: reject non-positive and non-numeric values.
- Defaults: keep 30s and 2 retries.

OPEN-DECISIONS: 3
