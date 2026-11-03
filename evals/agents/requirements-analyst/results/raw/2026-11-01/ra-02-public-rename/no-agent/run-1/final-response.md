## What the repository establishes

- `fetch(user_id: int) -> dict` is defined in `src/userclient/client.py:14`. It GETs `/users/{id}` and returns the parsed JSON.
- It is re-exported from `src/userclient/__init__.py` and listed in `__all__`.
- `src/userclient/sync.py` imports and calls it inside `sync_all`.
- `docs/api.md:8` lists `userclient.fetch(user_id)` as **stable**. The same file says names listed there follow semantic versioning, and that a breaking change waits for the next major release.
- The package is at version 2.1.0 (`pyproject.toml`), so the next major release is 3.0.
- No tests reference `fetch`. The only test covers `build_url`, which is marked internal.
- No other `fetch` references exist in the repo. Outside callers can't be seen from here.

## What the request leaves undecided

1. **Compatibility.** A plain rename removes a stable public name in a minor or patch release. That breaks the documented promise and any downstream callers. The request doesn't say which of these it wants:
   - **(a)** A hard rename, held for 3.0.
   - **(b)** A rename now, with `fetch` kept as a deprecated alias that emits a `DeprecationWarning`, and removal in 3.0.
   - **(c)** A hard rename now, deliberately breaking the policy, with a major version bump.
2. **Scope of the rename.** I assume it means the public function and all in-repo references. Those are `client.py`, `__init__.py` and its `__all__`, the `sync.py` import and call, and `docs/api.md`. The request doesn't say whether the docs row should change, or whether a changelog or migration note is wanted. The repo has no changelog.
3. **Version.** Whether to bump the version, and to what, depends on decision 1.

Decision 1 can't be settled from the repo. Only the requester, or whoever owns the release policy, can make it. Decisions 2 and 3 follow from it.

## What has to be settled first

Which compatibility path (a, b, or c) the requester wants. Once that is known, the change itself is small and mechanical.

OPEN-DECISIONS: 1
