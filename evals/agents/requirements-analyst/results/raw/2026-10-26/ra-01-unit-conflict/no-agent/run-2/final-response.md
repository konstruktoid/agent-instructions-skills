## What the repository establishes

- **The timeout is already configurable, in one way.** `src/fetchkit/config.py:5` sets `TIMEOUT_MS = int(os.environ.get("FETCHKIT_TIMEOUT_MS", "30000"))`. It is read once at import, in **milliseconds**, with a default of 30000.
- **How it is used.** `src/fetchkit/client.py:13` passes `config.TIMEOUT_MS / 1000` to `urlopen`. That is a per-attempt socket timeout. `get()` makes `RETRIES + 1` attempts, and `RETRIES` defaults to 2 via `FETCHKIT_RETRIES`. So the worst case before `RuntimeError` is about 90 seconds, not 30.
- **The README disagrees with the code on units.** `README.md:7-8` says the batch runner's `--timeout` option takes **seconds**, so `--timeout 5` gives up after five seconds. The only existing knob is the env var, which takes **milliseconds**.
- **No `--timeout` option exists.** The repo has no batch runner and no CLI or argparse code. It contains only `__init__.py`, `client.py` and `config.py`. The README describes something this repo doesn't contain. The runner is either in another repo or doesn't exist yet.
- **No tests, and `get(url)` takes no timeout parameter.** Callers can only change the timeout through the environment, before import.
- **The README is also loose on the 30-second claim.** It says "Every request times out after 30 seconds". With retries, that holds per attempt, not per call.

## What the request leaves undecided

"Make the timeout configurable" is ambiguous because a configuration path already exists. "Keep existing behaviour" is ambiguous because the two sources of "existing behaviour" conflict.

1. **Unit conflict.** The env var is in ms and the documented `--timeout` is in seconds. The request doesn't say which is authoritative, or whether both must coexist. Keeping existing behaviour can't mean both if they share one setting. For example, `FETCHKIT_TIMEOUT_MS=5` means 5 ms, while `--timeout 5` means 5 s.
2. **What "configurable" adds.** It could mean any of these:
   - the missing `--timeout` runner option;
   - a per-call `get(url, timeout=...)` parameter;
   - reading the value at call time instead of import time;
   - something else.
3. **Where the runner lives.** If `--timeout` belongs to a runner outside this repo, this change may only be able to expose a parameter, with the CLI wiring done elsewhere.
4. **What the timeout covers.** It is currently per attempt. It is unclear whether the configurable value should stay per attempt or become a total deadline across retries. A total deadline would change behaviour.
5. **Validation.** Today there is none. Zero, negative or non-numeric values are not checked, and a bad env value raises `ValueError` at import. The request doesn't say whether to keep or change that.

## What has to be settled first

Only the requester can decide these:

1. **Unit and source of truth.** Should the setting be seconds (matching the README), or milliseconds (matching the code and env var)? If seconds, `FETCHKIT_TIMEOUT_MS` must be kept as a compatibility alias or deprecated. The README or the code must be corrected either way.
2. **Surface to add.** Should it be a CLI `--timeout` (and where does that runner live), a function parameter, or both?
3. **Per-attempt or total.** This determines whether retries multiply the effective timeout, as they do now.

Details such as validation messages and the precedence order (argument over env over default) can be proposed by the implementer and confirmed in review. I count them as defaults, not blockers.

OPEN-DECISIONS: 3
