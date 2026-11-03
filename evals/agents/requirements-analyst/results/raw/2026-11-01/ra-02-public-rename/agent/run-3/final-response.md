# Requirements analysis: rename `fetch` to `fetch_user`

## Established facts

- `fetch(user_id: int) -> dict` is defined in `src/userclient/client.py:14`.
- `src/userclient/__init__.py` re-exports it and lists it in `__all__` (lines 3 and 6).
- `src/userclient/sync.py` imports it (line 3) and calls it (line 11).
- `docs/api.md:8` lists `userclient.fetch(user_id)` as **stable**. The same file says (lines 3-4) that a breaking change to a listed name "waits for the next major release".
- `pyproject.toml` sets the version to `2.1.0`, so the next major release is 3.0.0.
- `README.md` points to `docs/api.md` as the supported surface.
- `tests/test_client.py` tests only `build_url`. No test references `fetch`.
- Searching the working tree for `\bfetch\b` found no other references. There is no changelog, deprecation helper, or in-repo consumer beyond `sync.py`.

## Contradiction

The request is a plain rename of a public, stable name. The repository's own policy forbids a breaking change to that name before the next major release. A direct rename in a 2.x release would break every external caller of `userclient.fetch`. The request does not say which should prevail: the rename or the compatibility promise.

## Assumptions

- Confirmed: the `fetch` the request means is `userclient.client.fetch`, since it is the only definition.
- Confirmed: the rename touches the definition, the re-export, `__all__`, the `sync.py` import and call, and the `docs/api.md` row.
- Unresolved: whether external consumers of `userclient.fetch` exist. The repository describes an "internal user service" library, but I found no evidence either way.
- Unresolved: whether the request authorizes a major release. The request does not mention one.

## Decisions only the requester can make

1. **Compatibility strategy.** The options are:
   - (a) A breaking rename with a bump to 3.0.0.
   - (b) Add `fetch_user` and keep `fetch` as a deprecated alias in 2.x. Removal then waits for 3.0.0.
   - (c) Defer the rename until a major release is planned.

   This is the blocking decision.
2. **Version and release handling.** Under (a), who bumps `pyproject.toml` and when? Under (b), what deprecation warning and removal target apply? No changelog exists, so should one be created?

Items I consider implementation details and not requester decisions: updating `sync.py` and the tests, and whether `fetch` stays in `__all__` during a deprecation period (this follows from decision 1).

## Proposed acceptance criteria

These hold under any strategy:
- `userclient.fetch_user(user_id)` exists, with the same signature and behavior as the current `fetch`.
- `fetch_user` is in `__all__`, and `sync.py` calls it.
- `docs/api.md` lists `fetch_user` as stable.

These depend on the strategy chosen:
- Under (a), `userclient.fetch` no longer exists, the version is `3.0.0`, and no reference to `fetch` remains.
- Under (b), `userclient.fetch` still works and emits a `DeprecationWarning`. `docs/api.md` marks it deprecated with a removal target. A test covers both the alias and the warning.
- A new test covers `fetch_user`, for example by mocking `urllib.request.urlopen`. The current suite would not detect a broken rename.
- The existing `test_build_url` still passes, and `import userclient` succeeds.

## Risks

- A direct rename breaks external callers silently at import time. The `ImportError` surfaces only when they upgrade.
- The test suite has no coverage of `fetch`, so a missed reference would go unnoticed without a new test.
- Git history and sibling repositories were not searched for consumers.

## Recommended next action

Ask the requester to choose among options (a), (b), and (c), and to confirm the version and release handling. Then implement the rename with the matching tests and documentation. Because the repository's compatibility policy points to (b) as the default within 2.x, the safest proposal to put to the requester is (b). That choice remains the requester's.

OPEN-DECISIONS: 2
