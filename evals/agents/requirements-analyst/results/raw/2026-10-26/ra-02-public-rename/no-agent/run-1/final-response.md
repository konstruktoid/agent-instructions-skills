## Analysis: rename `fetch` to `fetch_user`

I changed no files.

### What the repository establishes
- `fetch(user_id: int) -> dict` is defined at `src/userclient/client.py:14`. It makes an HTTP GET to the user service and returns the parsed JSON.
- The only other code uses are `src/userclient/sync.py:3` and `:11`, where `sync_all` calls it. There are no other references to `fetch` anywhere in the repo.
- `src/userclient/__init__.py:3,6` re-exports it and lists it in `__all__`. That makes `userclient.fetch` part of the top-level package surface.
- `docs/api.md:8` lists `userclient.fetch(user_id)` as **stable**. The same file says names in this table follow semantic versioning, and "a change that breaks one waits for the next major release."
- `pyproject.toml` has version **2.1.0**, so the next major release would be 3.0.0. `README.md` says `docs/api.md` documents the supported surface.
- `tests/test_client.py` only tests `build_url`. No test covers `fetch` or `sync_all`, so nothing would catch a broken rename.

### The conflict
A plain rename removes `userclient.fetch`, which is a stable public name. By the project's own policy, that has to wait for 3.0.0. The request doesn't say whether to follow that policy or override it. The internal call sites are trivial to update. The decision about external callers is the part that matters.

### What the request leaves undecided
1. **Release and compatibility strategy.** The options are:
   - (a) Hard rename now, which breaks the policy, would need a major version bump to 3.0.0, and would need the docs updated.
   - (b) Add `fetch_user` and keep `fetch` as a deprecated alias, for example with a `DeprecationWarning`. Remove `fetch` in 3.0.0. This is compatible with the policy.
   - (c) Defer the whole rename to the 3.0.0 cycle.

   Only the requester or maintainer can choose, because it depends on whether they will accept a breaking release.
2. **Alias details, if (b) is chosen.** Whether the alias should warn, and which version removes it. These can be settled once the strategy is picked.

### Decisions that can be made without the requester
These follow from the repo:
- `fetch` is the only function with that name. The rename should cover the definition, the `__init__` import and `__all__`, and the `sync.py` import and call. It should also update `docs/api.md`.
- A `fetch_user` test is worth adding, since none exists. It would need `urlopen` mocked.
- `build_url` and `BASE_URL` stay as they are.

### What has to be settled first
The requester must say which compatibility strategy to use. Without that, implementation could break a documented stable API.

OPEN-DECISIONS: 1
