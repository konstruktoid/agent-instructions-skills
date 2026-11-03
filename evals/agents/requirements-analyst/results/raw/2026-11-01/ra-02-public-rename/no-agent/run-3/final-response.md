## Current behavior (from the repo)

- `fetch(user_id: int) -> dict` is defined in `src/userclient/client.py:14`. It GETs `{BASE_URL}/users/{id}` and returns the parsed JSON.
- It is re-exported from `src/userclient/__init__.py:3`, and `"fetch"` is in `__all__` (line 6).
- It is used internally in `src/userclient/sync.py:3` (import) and `:11` (`CACHE[user_id] = fetch(user_id)`).
- `docs/api.md:8` lists `userclient.fetch(user_id)` as **stable**. The page says names listed there follow semantic versioning, and a breaking change waits for the next major release.
- `pyproject.toml` has version **2.1.0**, so the next major is 3.0.0.
- `tests/test_client.py` only covers `build_url`, which is documented as internal. No test references `fetch`. `README.md` doesn't mention it.
- No other file in the repo mentions `fetch`. I can't see external callers.

## What the request leaves undecided

1. **Compatibility policy.** A plain rename removes a documented stable public name in a minor-version line (2.1.0). That conflicts with the repo's stated promise. The request doesn't say which of these is wanted:
   - (a) A hard rename that breaks the promise, released as 3.0.0 or as an accepted exception.
   - (b) Rename plus a deprecated `fetch` alias, for example one that emits `DeprecationWarning`. This is compatible, and the alias is removed in 3.0.
   - (c) Defer the rename until the next major release.

   Only the requester can choose between these, since it's a release and ownership call.
2. **Version and changelog.** If the removal is immediate, should the version be bumped, and to what? The repo has no changelog.

## Settled by the repo (no decision needed)

- The scope of the change is the definition, the `__init__` import and `__all__`, the `sync.py` import and call, and the `docs/api.md` row. The docs row should say `fetch_user`, and if an alias is kept, it should be listed as deprecated.
- `build_url` and `sync_all` stay as they are. The request doesn't mention them.
- The docstring and behavior are unchanged.
- No existing test needs updating. A test for the new name, and for the alias if one is kept, would be worth adding.

## What has to be settled first

Which compatibility path applies: hard break, deprecated alias, or wait for 3.0. Everything else follows mechanically from that choice.

OPEN-DECISIONS: 1
