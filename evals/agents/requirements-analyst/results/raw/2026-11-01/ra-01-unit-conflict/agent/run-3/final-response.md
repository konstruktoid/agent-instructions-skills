# Requirements analysis: "Make the timeout configurable and keep existing behaviour"

## Established facts
- `src/fetchkit/config.py:5` already reads `TIMEOUT_MS` from the environment variable `FETCHKIT_TIMEOUT_MS`. The default is `30000`, and the value is in milliseconds. It is read once at import. `RETRIES` is read the same way, with a default of 2 (`config.py:6`).
- `src/fetchkit/client.py:13` passes `config.TIMEOUT_MS / 1000` to `urlopen`. `get(url)` takes no timeout parameter.
- `client.py:11-17` makes up to `RETRIES + 1` attempts, which is 3 by default. Each attempt gets the full timeout. It catches `OSError` and then raises `RuntimeError`.
- `README.md:7-8` says every request times out after 30 seconds. It also says the batch runner's `--timeout` option takes **seconds**, so `--timeout 5` gives up after five seconds.
- The repository has no batch runner, no `--timeout` option, no CLI code and no tests. The only files are `__init__.py` (exports `get`), `client.py`, `config.py`, `README.md` and `pyproject.toml`. `pyproject.toml` has no entry points.

## Findings
1. **The timeout is already configurable, but only in a limited way.** It is set through an environment variable, once, for the whole process. The request could mean any of these:
   - (a) a per-call argument, such as `get(url, timeout=...)`;
   - (b) the `--timeout` CLI option described in the README, which does not exist in this repository;
   - (c) a change to the existing environment variable;
   - (d) a way to change it at runtime.
2. **The units conflict.** The code and environment variable use milliseconds. The README says `--timeout` takes seconds. A new knob has to pick one unit, and "keep existing behaviour" does not say which. If `--timeout 5` is passed into `TIMEOUT_MS` unconverted, it means 5 ms.
3. **"Existing behaviour" is ambiguous.**
   - The README promises "every request times out after 30 seconds". In the code, a single `get` call can take up to about 90 seconds before it fails (3 attempts × 30 s, plus any other delay). So it is unclear whether "behaviour" means the default per-attempt value of 30 s, the total time to failure, or the documented sentence.
   - The environment variable's name, unit and import-time read are also existing behaviour that callers may depend on.
4. **The batch runner is not in this repository.** It may live elsewhere, and it is not confirmed that it calls `get` or sets `FETCHKIT_TIMEOUT_MS`.

## Assumptions
- Confirmed: the default is 30 s, and the unit in code is milliseconds.
- Reasonable but unconfirmed: the existing environment variable should keep working unchanged.
- Unresolved: where the new configuration is supplied, its unit, whether it covers each attempt or the whole call, and what to do with invalid values.

## Proposed acceptance criteria
These depend on the decisions below.
1. With nothing configured, `get` uses a 30 s timeout per attempt, and the retry behaviour is unchanged.
2. `FETCHKIT_TIMEOUT_MS=5000` still produces a 5 s timeout.
3. The new configuration path produces the requested timeout, with its unit stated in the code and the README.
4. The README and the code agree on the unit and the scope of the timeout.
5. Invalid values (zero, negative, non-numeric) behave as specified. Today a non-numeric value raises `ValueError` at import, and zero or a negative value is passed to `urlopen` without a check.
6. Verification: there are no tests today, so add tests that patch `urlopen` and check the `timeout` argument for the default, the environment variable and the new path. Tests are the only way to check these cases.

## Risks
- A seconds and milliseconds mix-up would give a 1000× error in either direction.
- Because `config.TIMEOUT_MS` is read at import, changing the environment later has no effect, and a per-call override can't be added without changing `get`'s signature.
- The retry multiplier makes the real worst-case wait three times the configured value.

## Open decisions (requester only)
1. Where should the setting be configurable: a per-call argument, a CLI flag in a runner outside this repository, a changed environment variable, or several of these?
2. Which unit should the new setting use, seconds (as the README says) or milliseconds (as the code does)? Should the other one remain supported?
3. Should the timeout apply to each attempt or to the whole call including retries? "Keep existing behaviour" needs this answered.
4. How should invalid or zero values be handled: reject them, fall back to the default, or treat zero as "no timeout"?

## Recommended next action
Ask the requester these four questions. Also ask where the batch runner lives, because the README describes it but it isn't here. Only after that should anyone write code, in a minimal change that keeps the 30 s default and the `FETCHKIT_TIMEOUT_MS` behaviour.

OPEN-DECISIONS: 4
