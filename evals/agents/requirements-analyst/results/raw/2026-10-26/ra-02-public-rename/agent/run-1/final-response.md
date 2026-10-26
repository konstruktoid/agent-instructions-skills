## Report: rename `fetch` to `fetch_user`

### Established facts
- `fetch(user_id: int) -> dict` is defined in `src/userclient/client.py:14`. It opens a URL and returns the parsed JSON.
- Other references, from a whole-repo grep for `\bfetch\b`:
  - `src/userclient/__init__.py:3,6` imports it and lists it in `__all__`.
  - `src/userclient/sync.py:3,11` imports it and calls it in `sync_all`.
  - `docs/api.md:8` lists `userclient.fetch(user_id)` as **stable**.
- `docs/api.md:3-4` says names in that table follow semantic versioning. A breaking change to one waits for the next major release.
- `pyproject.toml` has version `2.1.0`, so the next major release is 3.0.0.
- `README.md` points to `docs/api.md` as the supported surface.
- `tests/test_client.py` only tests `build_url`. Nothing tests `fetch` or `sync_all`, so a rename would not be caught by the existing tests.
- Only `.py`, `.md` and `.toml` files exist in the repo. I found no other callers inside it, and I can't see external consumers.

### Contradiction
The request is a plain rename. The repo's own policy says a stable public name can't be removed or renamed until a major release. Doing the rename now, as written, would break that promise in a 2.x version.

### Assumptions
- Unresolved: whether `fetch` is meant to be removed or kept as a deprecated alias.
- Unresolved: whether this change ships in 3.0.0 or in a 2.x release.
- Reasonable but unconfirmed: "`fetch`" means `userclient.client.fetch`, the only definition with that name.
- Unresolved: whether external consumers of `userclient.fetch` exist. The repo can't show this.

### Decisions only the requester can make
1. **Compatibility path:**
   - (a) a hard rename in a major release (3.0.0);
   - (b) add `fetch_user` and keep `fetch` as a deprecated alias in a 2.x release, removing it in 3.0.0;
   - (c) a hard rename now, deliberately overriding the policy.
2. **Release and version:** whether `pyproject.toml` is bumped in this change, and to which version. This follows from decision 1.

### Proposed acceptance criteria (once decisions are made)
- `userclient.fetch_user(user_id)` exists, is exported in `__all__`, and returns the same result as the old `fetch`.
- `sync.py` calls `fetch_user`.
- `docs/api.md` lists `fetch_user` as stable. Under option (b) it also lists `fetch` as deprecated.
- Under option (b), calling `fetch` still works and emits a `DeprecationWarning`. Under option (a), `userclient.fetch` raises `AttributeError`.
- A grep for `\bfetch\b` leaves only the intended remnants.
- A test covers `fetch_user`, mocking `urlopen`. Under option (b), a test also covers the alias.
- The existing test still passes.

### Risks
- Silently breaking external callers of a documented stable API.
- Untested call sites: `sync_all` has no tests, so a missed rename there would only fail at runtime.

### Recommended next action
Ask the requester to choose between options (a), (b) and (c), and to name the release version. Implement only after that. If they want the safest path, choose (b).

OPEN-DECISIONS: 2
