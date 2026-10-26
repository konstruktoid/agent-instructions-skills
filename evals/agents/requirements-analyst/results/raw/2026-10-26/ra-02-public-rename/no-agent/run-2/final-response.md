## What the repository establishes

- `fetch(user_id: int) -> dict` is defined in `src/userclient/client.py:14`. It GETs `{BASE_URL}/users/{id}` and returns the parsed JSON.
- It is re-exported in `src/userclient/__init__.py:3` and listed in `__all__` at line 6.
- It is used internally in `src/userclient/sync.py:3` (import) and `sync.py:11` (call in `sync_all`).
- `docs/api.md:8` lists `userclient.fetch(user_id)` as **stable**. The same file says names listed there follow semantic versioning, and a breaking change waits for the next major release.
- The package is at version **2.1.0** (`pyproject.toml`). The next major release would be 3.0.0.
- `tests/test_client.py` only tests `build_url`, which is internal. No test references `fetch`.
- No other code, README text or config refers to `fetch`. I searched only this repo, so I can't see outside callers.

## What the request leaves undecided

The request is ambiguous only because `fetch` is a documented stable public name. A plain rename would remove `userclient.fetch`. That breaks any external caller and contradicts the stated compatibility promise in a minor or patch release.

1. **Compatibility strategy.** The request doesn't say which of these to do:
   - (a) Hard rename now. This breaks the semver promise, so it would need to ship as 3.0.0.
   - (b) Add `fetch_user` and keep `fetch` as a deprecated alias, probably with a `DeprecationWarning`. Then remove `fetch` in the next major release. This is compatible with the promise and could ship as a 2.x minor release.
   - (c) Defer the rename until a major release is planned.
2. **Version and release.** If (a) is chosen, does the requester want the version bumped to 3.0.0 in this change? If (b), does the requester want a minor bump (2.2.0), and which release removes the alias?
3. **Scope of the docs.** `docs/api.md` must change. Under (b) it needs a row for `fetch_user` as stable and a row for `fetch` as deprecated. There is no changelog file, so it's unclear whether one should be created.

## What has to be settled first

Item 1 only the requester can decide. It determines the code, docs, version and tests. Items 2 and 3 follow from it, so I'm not counting them separately. Internal details are not open: `sync.py` and `__init__.py` get updated, and a test for the new name is needed.

OPEN-DECISIONS: 1
