# Requirements analysis: make the timeout configurable and keep existing behaviour

## Established facts

1. **A timeout setting already exists, and it is configurable through the environment.** `src/fetchkit/config.py:5` sets `TIMEOUT_MS = int(os.environ.get("FETCHKIT_TIMEOUT_MS", "30000"))`. The module docstring says settings are "read once at import".
2. **The unit is milliseconds.** `client.py:13` passes `config.TIMEOUT_MS / 1000` as `timeout=` to `urllib.request.urlopen`.
3. **The timeout applies per attempt, not per call.** `client.py:11` loops `RETRIES + 1` times. `RETRIES` defaults to 2, so a call makes up to 3 attempts. The worst-case wait is about 90 s at the default. `OSError` triggers a retry, and a timeout is an `OSError`. After the last attempt the code raises `RuntimeError`.
4. **`get(url)` takes no timeout parameter.** It is the only public export (`__init__.py`).
5. **The README says the batch runner has a `--timeout` option, in seconds.** `README.md:7-8` documents `--timeout 5` as five seconds. The README also says "Every request times out after 30 seconds".
6. **The repository contains no batch runner and no `--timeout` code.** A search for "timeout" finds only `config.py`, `client.py` and the README. There are also no tests and no other callers.

## Contradiction

The README documents `--timeout` in seconds. The only implemented setting, `FETCHKIT_TIMEOUT_MS`, is in milliseconds. If a runner outside this repository forwards `--timeout 5` into `TIMEOUT_MS` unconverted, the result is 5 ms. If it converts the value, the units are consistent. The repository cannot show which is the case.

The README's "Every request times out after 30 seconds" is also inexact. It is true per attempt at the default, but not per `get` call (fact 3).

## What "configurable" could mean

- The request may be about the environment variable that already exists, which means a part may already be done.
- It may mean a per-call argument, such as `get(url, timeout=...)`.
- It may mean the `--timeout` option, whose code is not in this repository.
- It may mean a change to when the value is read. Today it is read at import, so changing it later in the process has no effect.

## Proposed acceptance criteria

These are conditional on the decisions below.

1. With no new input supplied, `get` calls `urlopen` with `timeout=30.0`, as it does now. If `FETCHKIT_TIMEOUT_MS` is set, behaviour is unchanged.
2. The retry count, the retried exception class and the final `RuntimeError` with its chained cause are unchanged.
3. The chosen new input, when supplied, overrides the default and the environment variable according to a stated precedence.
4. The unit of every new input is stated in its name or documentation, and the README matches the code.
5. Behaviour for an invalid value (zero, negative, non-numeric) is specified and tested.
6. Tests cover the default, the environment override and the new input. The repository has none today, so a test setup is needed.

## Unresolved decisions (requester only)

1. **Scope.** Is the existing environment variable enough, or is a new mechanism wanted? If new, which one: a `get()` parameter, a client object, or a change to when the value is read? Without this, the request may describe work that is already done.
2. **Unit.** Is a new input in seconds, as the README documents for `--timeout`, or in milliseconds, as `FETCHKIT_TIMEOUT_MS` is? Either choice leaves one of the two existing surfaces inconsistent. The README and the code already disagree.
3. **Meaning of "existing behaviour".** Does it mean that the 30 s default and the `FETCHKIT_TIMEOUT_MS` name and unit stay as they are? Does it also include the per-attempt timeout with 2 retries? Or does it mean the behaviour the README describes, a 30 s limit on the whole request?
4. **Where the `--timeout` runner lives.** The runner is outside this repository. Is changing it in scope, or only this library?

I count four decisions. Point 3 might have a reasonable default, which is to preserve the code as it stands. I am treating it as open because the README describes different behaviour.

## Risks

- Passing seconds into a millisecond setting would cut timeouts by a factor of 1000. Passing milliseconds into a seconds setting would lengthen them by the same factor.
- The retries make the worst-case wait up to three times the stated timeout. A user who sets `--timeout 5` may expect a 5 s limit and get up to 15 s.
- Because the value is read at import, a runner that parses `--timeout` after importing `fetchkit` cannot affect it through the environment.
- Adding a required parameter to `get` would break existing callers. Any new parameter must be optional.

## Recommended next action

Ask the requester the four questions above, starting with the unit and the scope. Do not implement before they answer. If they confirm that only a library-level, backward-compatible option is wanted, a small optional change is possible, with tests and a README correction.

OPEN-DECISIONS: 4
