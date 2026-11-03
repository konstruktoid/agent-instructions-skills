## What the repository establishes

- **The timeout is already configurable, in one way.** `src/fetchkit/config.py:5` reads `TIMEOUT_MS` from the `FETCHKIT_TIMEOUT_MS` environment variable. The default is `30000`, and the value is in **milliseconds**. It is read once, at import, and applies process-wide.
- **How it is used.** `client.get(url)` (`client.py:13`) passes `TIMEOUT_MS / 1000` to `urlopen`. `get` takes no timeout parameter.
- **Retries multiply the wait.** `RETRIES` defaults to 2, so each call makes up to 3 attempts. The worst case for one `get` is about 90 s at the default, not 30 s. Any `OSError` triggers a retry, and a socket timeout is an `OSError`.
- **The README conflicts with the code on units.** `README.md:7-8` says the batch runner has a `--timeout` option in **seconds**, and that `--timeout 5` gives up after five seconds. The environment variable is in milliseconds.
- **The `--timeout` option doesn't exist in this repo.** The repository has only `__init__.py`, `client.py` and `config.py`. There is no batch runner, no argument parsing, and no tests. I can't tell whether the runner lives in another repository or whether the README describes something that was never built.
- The README also says "every request times out after 30 seconds". That ignores retries and the env override.

## What the request leaves undecided

"Make the timeout configurable" has no clear gap to fill, because a configuration mechanism already exists. The request could mean any of these:
1. Add a per-call argument, such as `get(url, timeout=...)`.
2. Add the `--timeout` CLI option the README describes, in a runner that isn't here.
3. Fix the docs so they describe the existing env var.
4. Make the setting readable at runtime instead of once at import.

"Keep existing behaviour" is also ambiguous. It could mean any of these:
- A 30 s default.
- The env var keeps working in milliseconds.
- The retry behaviour stays as it is.
- The README's seconds semantics stay as written.

The last two can't both hold. A `--timeout` in seconds and `FETCHKIT_TIMEOUT_MS` in milliseconds are two sources for one setting with different units. If both are supported, the precedence between them is also undefined.

## What has to be settled first

1. **Which interface is wanted?** The options are a function argument, a CLI flag, a runtime-readable config, or docs only. Only the requester knows the intended gap.
2. **What unit does any new interface use?** The choice is seconds, as the README says, or milliseconds, as the code does. This can't be derived from the repo, because the two sources disagree. A user who passes `--timeout 5` into a millisecond setting would get a 5 ms timeout.
3. **Where is the batch runner?** If it is external, I need to know whether it's in scope. If it doesn't exist, I need to know whether to build it.
4. **Is the timeout per attempt or total across retries?** Today it is per attempt. Should that stay, with retries unchanged?
5. **Precedence and validation, if there are several sources.** If a flag, argument and env var can all be set, I need the order. I also need to know what happens with zero, negative or non-numeric values. Today a bad env value raises `ValueError` at import.

Two points are lower risk. I'd keep the 30000 ms default and the retry loop as they are under "existing behaviour". The README should be corrected whichever way decision 2 goes.

OPEN-DECISIONS: 3
