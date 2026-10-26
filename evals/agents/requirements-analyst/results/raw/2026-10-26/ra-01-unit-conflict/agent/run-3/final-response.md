# Requirements analysis: "Make the timeout configurable and keep existing behaviour"

## Established facts

- **A timeout setting already exists.** `src/fetchkit/config.py:5` reads `TIMEOUT_MS` from the environment variable `FETCHKIT_TIMEOUT_MS`. The default is `"30000"`, and the value is in milliseconds. The module docstring says settings are "read once at import".
- **The client divides the value by 1000.** `src/fetchkit/client.py:13` passes `config.TIMEOUT_MS / 1000` to `urlopen`, so the value is in seconds there.
- **Retries multiply the effective wait.** `RETRIES` defaults to 2 (`FETCHKIT_RETRIES`). The loop at `client.py:11` makes `RETRIES + 1`, so three attempts. Each attempt gets the full timeout, so worst-case time before `RuntimeError` is about 90 s by default.
- **The README states a different unit.** `README.md:7-8` says every request times out after 30 seconds. It also says the batch runner's `--timeout` option takes seconds, so `--timeout 5` gives up after five seconds.
- **No `--timeout` option exists in the repository.** The only match for `--timeout`, `argparse`, `click` or `__main__` is the README text. There is no batch runner, no tests, and no other code path that sets the timeout. `pyproject.toml` has no entry points or dependencies.
- **Only one public function exists.** `fetchkit.get(url)` takes no timeout parameter (`__init__.py`).

## Interpretation of the request

"Configurable" is already partly true through the environment variable. The request therefore does not say which gap it means to close. Candidates:

1. A per-call `timeout` parameter on `get`.
2. The documented `--timeout` CLI option, which is described but absent here. The runner may live in another repository.
3. Documentation of the existing environment variable.
4. A runtime change, since config is read once at import.

"Keep existing behaviour" is ambiguous because the repository holds two conflicting statements of the existing behaviour:

- The code's `FETCHKIT_TIMEOUT_MS` is in milliseconds.
- The README's `--timeout` is in seconds.

A new setting that follows either convention would contradict the other. The unit is the central conflict.

## Assumptions

| Assumption | Status |
|---|---|
| The default timeout stays at 30 s per attempt | Confirmed by code (`30000` ms) |
| `FETCHKIT_TIMEOUT_MS` must keep working in milliseconds | Reasonable but unconfirmed. Existing jobs may set it. |
| The README claim "every request times out after 30 seconds" is accurate | Contradicted. Retries make the total wait up to 90 s, and the environment variable can change the value. |
| A batch runner with `--timeout` exists | Unresolved. It is not in this repository. |
| Anything outside this repository sets `FETCHKIT_TIMEOUT_MS` | Unresolved |

## Proposed acceptance criteria

These apply once the decisions below are settled.

1. With no configuration set, `get` uses a 30 s per-attempt timeout, with the same retry count as today.
2. With only `FETCHKIT_TIMEOUT_MS=<n>` set, the timeout is `n` milliseconds, as today.
3. The new configuration path has one documented unit, and the name or documentation makes that unit unambiguous.
4. Precedence among a per-call argument, a CLI option, and the environment variable is stated and verified.
5. Invalid input (non-numeric, zero, negative) has defined behaviour. Today a non-numeric value raises `ValueError` at import.
6. The README matches the implemented behaviour, including the unit, retries, and where `--timeout` is implemented.
7. Verification covers the default, the environment override, and each new path. The repository has no tests, so the requester must say whether adding a test harness is in scope.

## Risks

- Adding a seconds-based option beside a milliseconds-based variable invites unit errors. A value of `5` read as milliseconds gives a 5 ms timeout, and `30000` read as seconds gives about 8 hours.
- "Fixing" the README to match the code, or the code to match the README, changes documented or relied-on behaviour either way.
- The read-once-at-import design blocks per-call or runtime changes unless that design changes. Changing it alters current behaviour.
- A timeout applied per attempt, not in total, may not be what the requester expects from "the timeout".

## Open decisions (requester only)

1. **Target surface:** per-call parameter, CLI option, runtime setter, or documentation of the existing variable, or a combination.
2. **Unit authority:** milliseconds (the code) or seconds (the README and `--timeout`), and whether the existing `FETCHKIT_TIMEOUT_MS` is kept unchanged.
3. **Location of the batch runner:** whether `--timeout` belongs in this repository or another one, and if another, whether this repository only needs to expose a parameter.
4. **Scope of the timeout:** per attempt (current) or total across retries.
5. **Invalid values and precedence:** how conflicting or invalid inputs resolve.

## Recommended next action

Ask the requester to settle decisions 1 and 2 first, since they determine the design. Then confirm decision 3. Do not implement before the unit is fixed, because the repository's two sources disagree.

OPEN-DECISIONS: 5
