## Report

### Established facts
- `fetch(user_id: int) -> dict` is defined in `src/userclient/client.py:14`. It requests `build_url(user_id)` and parses the JSON response.
- The repository references `fetch` in these places:
  - `src/userclient/__init__.py:3` imports it, and line 6 lists it in `__all__`, so `userclient.fetch` is re-exported.
  - `src/userclient/sync.py:3` imports it, and line 11 calls it inside `sync_all`.
  - `docs/api.md:8` lists `userclient.fetch(user_id)` as **stable**.
- `docs/api.md:3-4` says names listed there follow semantic versioning, and that a breaking change waits for the next major release.
- `pyproject.toml` has version `2.1.0`, so the next major release is 3.0.0.
- `README.md` points to `docs/api.md` as the supported surface.
- `tests/test_client.py` only tests `build_url`. No test covers `fetch`, `sync_all`, or the package exports, so nothing would catch a broken rename.
- I did not look for callers outside this repository. If other code uses `userclient.fetch`, the repository can't show it.
- I did not read `.agent-standards/instructions/minimal_change_instructions.md` or the other standards files. They may add constraints for the implementation.

### Interpretation of the request
"Rename `fetch` to `fetch_user`" is unambiguous about the target. `fetch` is the only symbol with that name. It is also a documented stable public API, so renaming it is a breaking change under the repository's own policy.

### Conflict
A plain rename removes `userclient.fetch`. That breaks the compatibility promise in `docs/api.md`, and it would ship in a 2.x version (currently 2.1.0) unless the release plan changes.

### Decisions only the requester can make
1. **Compatibility approach.** The options are:
   - (a) A hard rename, released as 3.0.0.
   - (b) Add `fetch_user` and keep `fetch` as a deprecated alias, removing it in the next major release.
   - (c) A hard rename now, accepting the break in a minor or patch release. This contradicts the documented policy.
2. **Release and version.** Does this change bump the version, and to what? Option (a) requires 3.0.0. Option (b) probably requires a minor bump.
3. **Deprecation details, if (b) is chosen.** Should the alias emit a `DeprecationWarning`? Should `fetch` stay in `__all__` and in the docs table, marked deprecated?

### Proposed acceptance criteria
- `userclient.fetch_user(user_id)` exists with the same signature and behavior as today's `fetch`.
- `sync_all` calls `fetch_user`.
- `__init__.py` imports and exports `fetch_user` in `__all__`.
- `docs/api.md` lists `fetch_user` as stable, with `fetch` handled as the chosen option requires.
- No stale `fetch` references remain, apart from the deliberate alias under option (b).
- The behavior of `fetch_user` and `sync_all` is covered by a test (mocking `urlopen`), and the existing test still passes.
- The version in `pyproject.toml` matches the chosen compatibility decision.

### Risks
- Unknown external callers of `userclient.fetch` would break under a hard rename.
- Without tests for `fetch`, `sync_all`, or the exports, a missed reference would only show up at runtime.
- The rename must not touch `build_url`, which is internal, or other unrelated names.

### Recommended next action
Ask the requester to choose between options (a), (b), and (c), and to confirm the version. After that, the change is small: three source files, the docs, and one added test.

OPEN-DECISIONS: 2
