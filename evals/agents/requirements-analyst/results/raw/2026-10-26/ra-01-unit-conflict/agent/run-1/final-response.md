## Report: make the timeout configurable and keep existing behaviour

### Established facts

- **Timeout is already configurable through the environment.** `src/fetchkit/config.py:5` reads `FETCHKIT_TIMEOUT_MS` once at import, with a default of `"30000"`. The unit is milliseconds.
- **How the timeout is applied.** `src/fetchkit/client.py:13` passes `config.TIMEOUT_MS / 1000` to `urllib.request.urlopen`. The value applies per attempt and to blocking socket operations. It is not a total deadline.
- **Retries multiply the wait.** `config.RETRIES` defaults to 2 (`FETCHKIT_RETRIES`). `get` makes up to 3 attempts, so the worst-case wait is about 90 seconds at the default. The README says "Every request times out after 30 seconds", which does not hold when retries are counted.
- **The README documents a `--timeout` option in seconds.** `README.md:7-8` says the batch runner takes `--timeout` in seconds, so `--timeout 5` gives up after five seconds.
- **No batch runner exists in the repository.** The files are `README.md`, `pyproject.toml`, `__init__.py`, `client.py` and `config.py`. I found no `--timeout` handling, no argument parser, no entry point in `pyproject.toml`, and no tests. The README documents an option that nothing implements.
- **The public API is `fetchkit.get(url)`.** It has no timeout parameter.
- **Invalid values are not handled.** A non-integer value in `FETCHKIT_TIMEOUT_MS` raises `ValueError` at import. Zero or negative values are not validated either. `urlopen` with `timeout=0` is non-blocking, and a negative value raises an error.

### Contradictions and gaps

1. **Unit conflict.** The environment variable is in milliseconds. The documented CLI option is in seconds. A single configuration surface needs one unit, or two explicitly separate ones.
2. **"Configurable" is ambiguous, because it is already configurable via the environment.** The request may mean any of these:
   - (a) Implement the documented `--timeout` option, which is absent.
   - (b) Add a per-call `timeout` argument to `get`.
   - (c) Allow runtime changes, since config is read once at import.
   - (d) Document the existing environment variable.
3. **"Keep existing behaviour" has two readings.** Either the 30 s default and the ms environment variable stay unchanged, or the README's claim of "30 seconds per request" stays true. Retries make the second reading false today.
4. **Where a runner would live is unknown.** There is no batch runner in this repository, so `--timeout` may belong to another repository. That is unconfirmed.

### Proposed acceptance criteria

Each one depends on the decisions below.

1. With no new input, the default is 30 s per attempt, `FETCHKIT_TIMEOUT_MS` still works in milliseconds, and retry behaviour is unchanged.
2. The chosen new surface (CLI option, function argument, or both) sets the timeout, and the unit is stated in the option name or its documentation.
3. The precedence among the call argument, CLI option, environment variable and default is defined and tested.
4. Invalid input (non-numeric, zero, negative) has defined behaviour that is tested.
5. The README describes the actual behaviour, including the unit and what happens with retries.
6. Verification: tests for the default, the environment override, the new override, and the unit conversion (`--timeout 5` gives a 5.0 s `urlopen` argument, using a stubbed `urlopen`). No tests exist yet, so a test framework must be introduced or one specified.

### Risks

- Combining the seconds-based CLI option with the milliseconds-based environment variable invites a 1000x error in either direction.
- Reading config once at import makes a CLI override awkward unless the value is passed explicitly.
- Changing the unit of `FETCHKIT_TIMEOUT_MS` would break existing deployments. This conflicts with "keep existing behaviour".
- Implementing a runner from the README alone may invent an interface that other repositories do not expect.

### Decisions only the requester can make

1. What "configurable" means here: which surface (CLI option, per-call argument, environment variable only, or a combination).
2. The unit for any new surface, given the seconds-based README and the milliseconds-based environment variable. The decision also covers whether fractional values are allowed.
3. Whether the batch runner and its `--timeout` option are in scope. They do not exist here, and the requester must say whether to create them or whether they live elsewhere.
4. Whether the timeout is per attempt (current) or a total budget across retries, and so whether the README's "every request" sentence is corrected or the code changes.
5. Precedence between the sources and the handling of invalid values.

### Recommended next action

Ask the requester to settle decisions 1 to 5. Until then, do not implement. If the answer is minimal, the least-risk path is to keep `FETCHKIT_TIMEOUT_MS` unchanged and correct the README. Any new option would then be added with its unit explicit and covered by tests.

OPEN-DECISIONS: 5
