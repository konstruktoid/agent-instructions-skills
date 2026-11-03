## Analysis: make the timeout configurable and keep existing behaviour

### What the repository establishes
- **The timeout is already configurable, in a limited way.** `src/fetchkit/config.py:5` reads `TIMEOUT_MS` from the `FETCHKIT_TIMEOUT_MS` environment variable. The default is `30000`, so 30 seconds. It is read once at import and is process-wide.
- **How it is used.** `client.get(url)` in `src/fetchkit/client.py:13` passes `TIMEOUT_MS / 1000` to `urlopen`. The value is a per-attempt socket timeout. `get` takes no timeout parameter.
- **Retries multiply the wait.** `RETRIES` defaults to 2, so there are up to 3 attempts. A failing request can take about 90 seconds in total. Any `OSError` triggers a retry, and a timeout is an `OSError`.
- **The unit conflict.** The README (lines 5-8) says the `--timeout` option of the batch runner takes **seconds**, and `--timeout 5` gives up after 5 seconds. The code uses **milliseconds** (`TIMEOUT_MS`).
- **No `--timeout` option exists here.** The repo contains only `README.md`, `pyproject.toml`, `__init__.py`, `client.py` and `config.py`. There is no batch runner, no CLI and no argument parsing. The runner is either in another repo or doesn't exist yet. There are no tests.
- **The README is also imprecise.** "Every request times out after 30 seconds" ignores retries and the environment override.

### What the request leaves undecided
1. **What "configurable" means.** It could mean:
   - a `timeout` parameter on `get()`;
   - the existing environment variable (which would make the request already done);
   - a `--timeout` CLI option in the batch runner, which is not in this repo;
   - a config file.

   The request doesn't say which.
2. **Unit.** The documented `--timeout` is in seconds. The existing environment variable is in milliseconds. A new knob needs one unit, and a wrong guess is a 1000× error. For example, `--timeout 5` passed through as milliseconds gives 5 ms.
3. **Where the runner lives.** The `--timeout` option can't be changed or checked from this repo. Whoever owns the runner has to convert units, or `fetchkit` must accept seconds.
4. **What "keep existing behaviour" covers.** It could mean:
   - the 30 s default;
   - the `FETCHKIT_TIMEOUT_MS` variable and its ms unit;
   - the documented seconds semantics of `--timeout`;
   - the retry multiplication.

   The README and the code disagree on units, so the existing behaviour is not one thing. Keeping both literally is impossible if they share a name.
5. **Total deadline vs per-attempt timeout.** Should the configured value cap each attempt, as now, or the whole call including retries?
6. **Validation.** Not specified: zero, negative, non-numeric, and `None` for no timeout. `int(...)` currently raises `ValueError` at import on a bad value, and fractional seconds can't be expressed in the ms integer.
7. **Precedence.** If both an argument and the environment variable are set, which one wins?

### What has to be settled first
- Which interface is being added, and who owns the batch runner.
- The unit of any new setting, and whether the README or the code is the source of truth. This is the key conflict.
- Whether the existing environment variable's ms semantics must stay unchanged, with a seconds-based option added alongside.

Decisions 1 to 4 can only come from the requester. Per-attempt vs total (5), validation (6) and precedence (7) have sensible defaults I could propose, such as per-attempt, reject non-positive values, and argument over environment variable. They are lower risk, but the requester should confirm them.

OPEN-DECISIONS: 4
