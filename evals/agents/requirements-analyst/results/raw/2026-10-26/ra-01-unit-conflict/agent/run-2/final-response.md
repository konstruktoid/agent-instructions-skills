# Requirements analysis: "Make the timeout configurable and keep existing behaviour"

## Established facts

- **Timeout already has an env setting.** `src/fetchkit/config.py:5` reads `TIMEOUT_MS` from `FETCHKIT_TIMEOUT_MS` once at import, with a default of `30000`. The unit is milliseconds.
- **Retries are also configurable.** `config.py:6` reads `RETRIES` from `FETCHKIT_RETRIES`, default `2`.
- **Where the timeout is used.** `src/fetchkit/client.py:13` passes `config.TIMEOUT_MS / 1000` to `urllib.request.urlopen`. `get(url)` has no timeout parameter.
- **Retry loop.** `get` makes `RETRIES + 1` attempts, so 3 by default. The timeout applies to each attempt, so the worst case is about 90 s of waiting before `RuntimeError`.
- **README states a different unit.** `README.md:7-8` says every request times out after 30 seconds. It also says the batch runner's `--timeout` option takes seconds, so `--timeout 5` gives up after five seconds.
- **No batch runner exists in this repository.** Only `README.md`, `pyproject.toml`, `__init__.py`, `client.py` and `config.py` are present. `--timeout` appears only in the README. No tests exist.
- **Nothing in the repository defines "configurable".** I did not read the git history.

## Contradiction and gap

- **Unit conflict.** The environment variable is in milliseconds and the documented CLI option is in seconds. A value of `5` means 5 ms through the environment and 5 s through `--timeout`. "Keep existing behaviour" cannot be applied to both without choosing one.
- **The request names no mechanism.** The environment variable already makes the timeout configurable. The request could mean any of these:
  - a per-call `timeout` argument on `get`;
  - the `--timeout` runner option, whose code is not here;
  - a change to the environment variable;
  - a fix so the README matches the code.
- **Import-time reading.** `config.py` reads the value once, so changing it later in the same process has no effect. Whether this matters is unstated.

## Assumptions

| Assumption | Status |
|---|---|
| The default of 30 s must remain. | Confirmed by code and README. |
| The default env var name `FETCHKIT_TIMEOUT_MS` must keep working. | Reasonable but unconfirmed. |
| The timeout is per attempt, not a total deadline across retries. | Confirmed for current code. Whether to preserve it is unresolved. |
| The batch runner is outside this repository. | Reasonable but unconfirmed. |

## Proposed acceptance criteria

These apply once the decisions below are settled.

1. With no configuration set, `get` still passes 30 s to `urlopen` and retries `RETRIES` times.
2. A caller can set the timeout through the chosen mechanism, and `urlopen` receives that value converted to seconds.
3. `FETCHKIT_TIMEOUT_MS=30000` (and any other existing value) behaves as before.
4. The README and the code state the same unit and the same precedence rule.
5. Invalid values (non-numeric, zero, negative) have a defined result, either an error or a fallback.
6. A test mocks `urlopen` and checks the timeout argument for the default, the env value and the new override.

## Risks

- Silently reinterpreting `FETCHKIT_TIMEOUT_MS` as seconds would turn existing deployments' `30000` into a very long timeout.
- Implementing `--timeout` in seconds against a millisecond setting invites a 1000-fold error.
- Applying the timeout as a total deadline would shorten the worst-case wait, which changes behaviour.

## Decisions only the requester can make

1. **Mechanism and scope.** State which interface is meant: a `get` argument, the `--timeout` runner option (and where that code lives), or both. Say whether the existing environment variable already satisfies the request.
2. **Unit and the README conflict.** State the unit the new setting uses (seconds or milliseconds). State whether the README or the environment variable's millisecond unit is the wrong one. If the README is wrong, the fix is a documentation correction.
3. **Precedence and semantics.** State the order of explicit argument, environment variable and default. State whether the timeout stays per attempt or becomes a total deadline.

## Recommended next action

Ask the requester the three decisions above before any edit. Once they are answered, the change is small: add an optional override in `get` or `config`, convert units in one place, and add the tests and README update.

OPEN-DECISIONS: 3
