# Requirements analysis: "Make the timeout configurable and keep existing behaviour"

## Established facts

- **The timeout is already configurable through the environment.** `src/fetchkit/config.py:5` sets `TIMEOUT_MS = int(os.environ.get("FETCHKIT_TIMEOUT_MS", "30000"))`. The default is 30000 ms.
- **The value is read once, at import.** The `config.py` docstring says "Process-wide settings, read once at import". Changing the environment variable later in the same process has no effect.
- **The client converts milliseconds to seconds.** `client.py:13` calls `urlopen(url, timeout=config.TIMEOUT_MS / 1000)`.
- **Each attempt gets the full timeout.** `client.py:11` loops `RETRIES + 1` times, and `RETRIES` defaults to 2. A failing request can therefore take up to 3 × 30 s = 90 s, plus any time before the first byte.
- **The public API is only `get(url)`.** It has no timeout parameter (`__init__.py`, `client.py:8`).
- **The batch runner and `--timeout` option do not exist in this repository.** A search for "timeout" finds only `README.md`, `client.py` and `config.py`. There is no CLI code, no tests, and no entry point in `pyproject.toml`.
- **The README contradicts the code.**
  - `README.md:7` says "Every request times out after 30 seconds", which ignores the retries and the environment variable.
  - `README.md:7-8` says `--timeout` takes **seconds** (`--timeout 5` means five seconds). The only existing configuration knob, `FETCHKIT_TIMEOUT_MS`, takes **milliseconds**.

## Reading of the request

"Configurable" has no clear target, because a configuration path already exists. The likeliest intents are:

1. Add a per-call or per-job override. This could be a `timeout` argument to `get()` or the `--timeout` runner option the README describes.
2. Make the existing setting more usable, for example by reading it at call time or by accepting seconds.
3. Reconcile the README with the code.

This is an inference. Nothing in the repository settles which one is meant.

## Assumptions

| Assumption | Status |
|---|---|
| Default behaviour must stay 30 s per attempt, with 2 retries. | Reasonable but unconfirmed. This is the likeliest meaning of "keep existing behaviour". |
| `FETCHKIT_TIMEOUT_MS` must keep working with the same name and unit. | Reasonable but unconfirmed. Other jobs may set it. |
| A `--timeout` runner exists somewhere else, outside this repository. | Unresolved. The README implies it, but no code here supports it. |
| The timeout applies per attempt, not to the whole call. | Confirmed by the code. Whether this is the intended meaning is unresolved. |

## Proposed acceptance criteria

These hold once the decisions below are settled.

1. With nothing configured, `get()` calls `urlopen` with `timeout=30.0` and retries `RETRIES` times, exactly as it does now.
2. With `FETCHKIT_TIMEOUT_MS=5000` set before import, the call uses `timeout=5.0`, as it does now.
3. The new configuration path takes a value in one documented unit. A value of "5" must yield exactly 5 s or 5 ms, never the other.
4. Invalid values (zero, negative, non-numeric) have defined behaviour that matches or deliberately changes the current `int()` failure at import. The choice is documented.
5. Precedence between the new path and the environment variable is defined and tested.
6. The README describes the actual behaviour, including the unit, the retries, and whether `--timeout` exists in this repository.
7. Tests verify the default, the environment override and the new path by checking the `timeout` value passed to a mocked `urlopen`. The repository has no tests today.

## Decisions only the requester can make

1. **The configuration surface.** The options are a `get(url, timeout=...)` parameter, a runner flag, an environment-variable change, or something else. The existing environment variable already counts as configurable.
2. **The unit.** `--timeout` is documented in seconds, but `FETCHKIT_TIMEOUT_MS` is in milliseconds. The requester must choose one of three:
   - The new input is in seconds.
   - It is in milliseconds.
   - Both are supported under distinct names.

   Either choice changes the README or the code. This also decides whether "keep existing behaviour" means the README's seconds claim or the code's milliseconds.
3. **Whether the runner is in scope.** The `--timeout` runner code is not in this repository. The requester must say where it lives, or whether it should be built here.
4. **What the timeout covers.** It could stay per attempt (up to 90 s in total by default), or become a total deadline. A total deadline would change existing behaviour.
5. **Whether `RETRIES` is covered.** The request says only "the timeout". Retries multiply the effective wait.

## Risks

- Choosing the wrong unit could make a "5" mean 5 ms and fail every request, or 5000 s and hang jobs.
- Reading the setting at call time instead of at import changes semantics for callers that rely on import-time freezing. This is low risk but is a behaviour change.
- The existing README is wrong in two places, so using it as the specification would encode the wrong behaviour.

## Recommended next action

Ask the requester to settle decisions 1–3 at minimum. Until then, no implementation is safe. A reasonable default to propose is a `timeout` keyword argument in seconds on `get()`, with the environment variable and its default unchanged. That proposal should be confirmed, not assumed.

OPEN-DECISIONS: 5
