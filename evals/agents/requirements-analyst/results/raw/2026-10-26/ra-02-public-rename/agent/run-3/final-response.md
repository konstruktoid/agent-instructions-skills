# Requirements report: rename `fetch` to `fetch_user`

## Established facts
- `fetch(user_id: int) -> dict` is defined in `src/userclient/client.py:14`.
- `src/userclient/__init__.py:3,6` imports it and lists it in `__all__`. So it is exported as `userclient.fetch`.
- `src/userclient/sync.py:3,11` imports and calls it inside `sync_all`.
- `docs/api.md:8` lists `userclient.fetch(user_id)` as **stable**. The same file says changes that break a listed name "wait for the next major release".
- `pyproject.toml` has version 2.1.0, so the next major release is 3.0.0.
- `README.md` points to `docs/api.md` as the supported surface.
- `tests/test_client.py` tests only `build_url`. No test covers `fetch`, `sync_all`, or the package export.
- A search for `\bfetch\b` found no other references. I did not search for dynamic uses, such as string-based lookups.
- I did not check git history or tags for released versions. I also did not look for consumers outside this repository.

## The conflict
The request reads as a simple internal rename. This repository documents `fetch` as a stable public name under a semver promise.

- A plain rename breaks every external caller of `userclient.fetch` in a minor or patch release (2.1.0 → 2.2.0 or 2.1.1). That breaks the documented promise.
- The request does not say whether to break the API, keep a compatibility alias, or wait for 3.0.0.

## Assumptions
- Confirmed: `fetch` is the function in `client.py`, and it has three in-repo references (the definition, the `__init__` export, the call in `sync.py`) plus one docs row.
- Reasonable but unconfirmed: `fetch_user` should have the same signature and behavior as `fetch`.
- Unresolved: whether `fetch` should keep working after the rename, and for how long.
- Unresolved: whether external consumers exist. The docs imply they do.

## Decisions only the requester can make
1. **Compatibility strategy.** Pick one:
   - (a) Hard rename now. This breaks the stable API and violates the documented policy.
   - (b) Add `fetch_user` and keep `fetch` as a deprecated alias. The alias would be removed in 3.0.0.
   - (c) Defer the rename to the 3.0.0 major release.
2. **Version and release plan.** Which version carries the change, and does the requester accept the semver implications? If the answer is (b), also decide whether `fetch` should emit a `DeprecationWarning`.

Whether `docs/api.md` should list `fetch_user` as stable is a follow-on to decision 1. It is not a separate decision.

## Proposed acceptance criteria
Final wording depends on decision 1. Under option (b), the likely recommendation, the criteria would be:
- `userclient.fetch_user(user_id)` exists, with the same signature and return behavior as `fetch`.
- `userclient.fetch` still works and is marked deprecated, with the removal version stated.
- `__all__` includes `fetch_user`. It includes `fetch` while the alias remains.
- `sync_all` calls `fetch_user`.
- `docs/api.md` documents `fetch_user` as stable and `fetch` as deprecated.
- Tests cover `fetch_user` and the alias, using a mocked `urlopen`, because none exist today.
- A search finds no remaining internal callers of the old name, other than the alias and its test.

Under option (a), drop the alias criteria and add a note in the docs and release notes that this is a breaking change. Under option (c), no code change happens now.

## Risks
- External callers break silently under option (a).
- No test would catch a broken export or a missing `sync_all` update, so the new tests are needed.
- The `userclient.fetch` docs row would be left stale if it isn't updated.

## Recommended next action
Ask the requester to choose the compatibility strategy and release plan. Because the request doesn't say, I suggest option (b) as the default. Do not implement until they answer.

OPEN-DECISIONS: 2
