# Requirements analysis: rename `fetch` to `fetch_user`

## Established facts
- `fetch(user_id: int) -> dict` is defined in `src/userclient/client.py:14`.
- `src/userclient/__init__.py:3,6` re-exports it and lists it in `__all__`, so `userclient.fetch` is the public import path.
- `src/userclient/sync.py:3,11` imports and calls it.
- `docs/api.md:8` lists `userclient.fetch(user_id)` as **stable**. The same file says (lines 3–4) that a change that breaks a listed name "waits for the next major release."
- `pyproject.toml` sets the version to 2.1.0, so the next major release is 3.0.0.
- `README.md` points to `docs/api.md` as the supported surface.
- `tests/test_client.py` only tests `build_url`. No test covers `fetch`, `sync_all`, or the package exports.
- A repository-wide search for `\bfetch\b` found no other references. I did not check git history or external consumers, and I did not read the `.agent-standards` files.

## Central conflict
A plain rename removes `userclient.fetch`. That breaks a stable, documented name in a minor or patch release, which the repository's own compatibility policy forbids. The request does not say whether to honor that policy or override it.

## Assumptions
- Confirmed: "`fetch`" means the function in `client.py`. It is the only definition.
- Reasonable but unconfirmed: the rename covers the function, its re-export, the `sync.py` call site, and the `docs/api.md` row.
- Unresolved: whether this release is a major version bump, and whether `fetch` should stay available as a deprecated alias.
- Unresolved: whether anyone outside this repository imports `userclient.fetch`. The repository cannot show this.

## Proposed acceptance criteria
These depend on the decisions below.
1. `userclient.fetch_user(user_id)` exists, has the same signature and behavior as the old `fetch`, and is in `__all__`.
2. `sync_all` calls `fetch_user`.
3. `docs/api.md` lists `fetch_user` as stable. Its treatment of `fetch` matches the chosen compatibility path.
4. Compatibility path, one of:
   - (a) `fetch` remains importable and emits a `DeprecationWarning`, and removal is deferred to 3.0.0.
   - (b) `fetch` is removed and the version is bumped to 3.0.0.
5. A new test covers `fetch_user`. Under path (a), it also covers the alias. The existing `build_url` test still passes.
6. A search for `\bfetch\b` returns only intentional leftovers, such as the alias or a deprecation note.

## Decisions only the requester can make
1. **Compatibility path.** Choose between keeping a deprecated `fetch` alias until 3.0.0 and removing it now with a major bump. The docs promise the former, and this decision overrides or confirms that promise.
2. **Release and versioning.** Decide whether `pyproject.toml` changes in this task, and to what version. This follows from decision 1.

If the requester chooses the alias, the alias details are an implementation choice. Those details are the warning category and the removal target.

## Risks
- Removing `fetch` outright breaks unknown external callers of a documented stable API.
- Test coverage is thin. Nothing would catch a broken export or a missed call site, so the new tests are needed.
- Git history, a changelog, and other consumers were not examined. A changelog or deprecation convention might exist elsewhere.

## Recommended next action
Ask the requester for decisions 1 and 2. If they have no preference, the safest default is path (a): add `fetch_user`, keep `fetch` as a deprecated alias, and update `sync.py`, `__init__.py`, and `docs/api.md`. Leave the version unchanged and defer removal to 3.0.0.

OPEN-DECISIONS: 2
