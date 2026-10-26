## Analysis: rename `fetch` to `fetch_user`

I changed no files.

### What the repository establishes
- `fetch(user_id: int) -> dict` is defined in `src/userclient/client.py:14`. It GETs `BASE_URL/users/{id}` and returns the parsed JSON.
- It is re-exported from `src/userclient/__init__.py:3` and listed in `__all__` (line 6). It is also imported and called in `src/userclient/sync.py:3,11`.
- `docs/api.md:8` lists `userclient.fetch(user_id)` as **stable**. The same file says stable names follow semantic versioning, and a breaking change "waits for the next major release".
- `pyproject.toml` has version **2.1.0**, so the next major release is 3.0.0.
- `build_url` is marked internal. `fetch` is not.
- No test references `fetch`. `tests/test_client.py` only covers `build_url`. Nothing in the repo uses `fetch` outside the files above. The README only points to `docs/api.md`.
- Other consumers of `userclient.fetch` may exist outside this repo, since it is a published library. The repo can't show that either way.

### What the request leaves undecided
A plain rename removes a stable public name in a 2.x release. That contradicts the repo's own compatibility promise. The request doesn't say how to handle that.

1. **Compatibility approach.** The options are:
   - (a) Rename now as a hard break. This conflicts with the documented policy unless it ships in 3.0.0.
   - (b) Add `fetch_user` and keep `fetch` as a deprecated alias, for example with a `DeprecationWarning`. The old name is removed in 3.0.0.
   - (c) Do the rename on a branch or change set held for the 3.0.0 release.
2. **Version bump.** The options are 2.2.0 for an additive change with a deprecation, 3.0.0 for a removal, or no bump yet. This depends on the answer to 1.
3. **Scope of "rename".** It is unclear whether `fetch_user` should also be exported in `__all__` and documented in `docs/api.md` as stable, and whether `fetch` stays listed there as deprecated. It is also unclear whether the internal names (`sync.py` import and call) should change. The internal updates are mechanical.

The following are not open decisions, because they follow from the repo:
- The signature and behavior stay the same.
- The call site in `sync.py` updates.
- The `__init__` export updates.
- The docs row updates.
- I'd add a test, since none exists for `fetch`.

### What must be settled first
The requester has to choose the compatibility approach (item 1). That choice determines the version bump (item 2) and what the docs say about the old name. Whether `fetch_user` should be documented as stable (item 3) is a smaller question that the requester can answer in the same reply.

OPEN-DECISIONS: 2
