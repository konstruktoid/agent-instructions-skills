## What the repository establishes

- **The timeout is already configurable, through the environment.** `src/fetchkit/config.py:5` sets `TIMEOUT_MS = int(os.environ.get("FETCHKIT_TIMEOUT_MS", "30000"))`. It is read once, at import, and it is in **milliseconds**. The default is 30000 ms, which is 30 s.
- **`client.get(url)` is the only consumer.** It passes `config.TIMEOUT_MS / 1000` to `urlopen` (`client.py:13`). `get` takes no timeout parameter.
- **The timeout applies to each attempt, not to the whole call.** `RETRIES` defaults to 2 (`FETCHKIT_RETRIES`), so `get` makes up to 3 attempts. With the defaults, a dead host can take about 90 s before `get` raises `RuntimeError`.
- **The README describes a different interface from the code.** It says "the `--timeout` option of the batch runner takes a number of seconds". The repository has no batch runner, no CLI, no argparse and no entry point in `pyproject.toml`. The only files are `README.md`, `pyproject.toml`, `__init__.py`, `client.py` and `config.py`. The runner presumably lives in another repository, and nothing here shows how it calls into fetchkit.
- **The README does not mention `FETCHKIT_TIMEOUT_MS`, retries, or the per-attempt behaviour.**
- **The code and the README use different units.** The code uses milliseconds and the README uses seconds. If `--timeout 5` were passed through to `TIMEOUT_MS` unconverted, it would mean 5 ms. Nothing in this repository does that conversion.
- **There are no tests.**

## What the request leaves undecided

"Make the timeout configurable" is ambiguous because a configuration mechanism already exists. "Keep existing behaviour" is ambiguous because the existing behaviour is described in two conflicting ways.

1. **What is missing from the current configurability?**
   - A per-call argument, such as `get(url, timeout=...)`?
   - A runtime or CLI setting that can change after import?
   - Support for the `--timeout` option the README describes?
   - Or only documentation of the existing env var?
2. **Which unit should the public interface use?**
   - The env var is in ms and the README's `--timeout` is in seconds.
   - A new parameter in either unit would contradict one of them.
   - Any new setting needs an explicit unit.
   - Whether `FETCHKIT_TIMEOUT_MS` keeps meaning milliseconds is part of the same decision.
3. **What does "existing behaviour" mean?**
   - Does it mean the code's behaviour: 30000 ms default, env var in ms, per-attempt timeout, 3 attempts?
   - Or the README's behaviour: 30 s and `--timeout` in seconds?
   - These agree on the default but not on the interface.
4. **What should the timeout cover?**
   - It is per attempt today, with retries.
   - Should a configured value stay per attempt, or become a total deadline across retries?
   - Changing this would break "keep existing behaviour".
5. **What should happen with invalid values?**
   - Examples are zero, negative or non-numeric values.
   - Today a non-numeric env var raises `ValueError` at import.
   - Whether `None` or 0 means "no timeout" is also undecided.
6. **Who else depends on this?** The external batch runner that owns `--timeout` may already set or translate the env var. I can't check that from here.

## What has to be settled first

- Where `--timeout` is implemented, and whether it is in scope for this change.
- The unit of any new interface.
- Whether "existing behaviour" follows the code or the README.
- Whether the timeout stays per attempt.

Decisions 1 to 4 can only be made by the requester. Invalid-value handling can follow existing conventions unless the requester says otherwise. Finding the batch runner is a fact-finding task, but the requester has to say whether it is in scope.

OPEN-DECISIONS: 4
