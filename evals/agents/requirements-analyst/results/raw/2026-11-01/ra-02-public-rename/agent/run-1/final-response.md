# Requirements analysis: rename `fetch` to `fetch_user`

## Established facts

- `fetch(user_id: int) -> dict` is defined at `src/userclient/client.py:14`. It requests `build_url(user_id)` and returns the parsed JSON.
- `src/userclient/__init__.py` imports `fetch` (line 3) and lists it in `__all__` (line 6). It is therefore re-exported as `userclient.fetch`.
- `src/userclient/sync.py` imports `fetch` (line 3) and calls it in `sync_all` (line 11). This is the only internal caller.
- `docs/api.md:8` lists `userclient.fetch(user_id)` as **stable**. The same file states that "a change that breaks one waits for the next major release."
- `README.md` points to `docs/api.md` as the supported surface.
- `pyproject.toml` sets the version to `2.1.0`, so the next major release would be 3.0.0.
- `tests/test_client.py` tests only `build_url`. No test covers `fetch`, `sync_all`, or the package export.
- A word-boundary search for `fetch` finds exactly the six occurrences above. No other file references it. The repository contains no changelog and no deprecation mechanism, such as a `warnings` helper.

## Central conflict

A plain rename removes `userclient.fetch`, which is a documented stable public name. By the repository's own policy, that break belongs in the next major release. The request does not say whether it is meant as that major-release change or whether the old name must keep working. The repository cannot answer this. Only the requester can.

## Assumptions

| Assumption | Status |
|---|---|
| "`fetch`" means the function in `client.py` and its re-export. | Confirmed by the search; it is the only definition. |
| No other repository imports `userclient.fetch`. | Unresolved. External consumers are invisible from here. |
| The `2.1.0` version is the released baseline. | Reasonable but unconfirmed. |
| The rename is intended to apply to the public export too, not just the internal module. | Unresolved. The request gives no scope. |

## Decisions only the requester can make

1. **Compatibility path.** Choose one of the following:
   - Remove `fetch` outright, as a breaking change in 3.0.0.
   - Keep `fetch` as a deprecated alias in 2.x, and remove it in 3.0.0.
   - Keep `fetch` indefinitely.

   The policy in `docs/api.md` excludes an outright removal in a 2.x release.
2. **Version bump.** State whether `pyproject.toml` should change in this work, and to which version. The repository has no stated release process.
3. **Deprecation behavior, if an alias is chosen.** Decide whether the alias emits a `DeprecationWarning` and on what removal timeline. No such convention exists here.

## Proposed acceptance criteria (conditional on decision 1)

- `userclient.fetch_user(user_id)` exists with the same signature and behavior as the current `fetch`.
- `client.py`, `__init__.py` (import and `__all__`), and `sync.py` use the new name.
- `docs/api.md` lists `fetch_user` as stable. The treatment of `fetch` matches the chosen compatibility path.
- Under an alias path, `userclient.fetch` still resolves and returns the same result as `fetch_user`. Under a removal path, `userclient.fetch` raises `AttributeError`.
- A test covers the new export. It should mock `urllib.request.urlopen` and check the returned dict and the URL requested. Another test covers `sync_all` calling the renamed function. Neither exists now.
- A search for `\bfetch\b` finds no stale reference, other than an intentional alias or deprecation note.
- Existing `test_build_url` still passes.

## Risks

- External callers of `userclient.fetch` break silently on upgrade if the removal ships in a minor or patch release.
- The lack of tests for `fetch` and `sync_all` means a missed reference would not be caught automatically. The `sync.py` import would fail at import time, which would also break `import userclient`.
- Running tests requires the package on the path (`src` layout). I did not run any tests because the request is analysis only and nothing was changed.

## Recommended next action

Ask the requester to decide the compatibility path and version handling (decisions 1 and 2). Implementation can then follow as a small change across the four files plus new tests.

OPEN-DECISIONS: 2
