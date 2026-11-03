## What the repository establishes

- `fetch(user_id: int) -> dict` is defined in `src/userclient/client.py:14`. It makes an HTTP GET to the user service and returns the parsed record.
- `fetch` is exported from the package: `src/userclient/__init__.py:3` imports it and `__all__` lists it.
- `src/userclient/sync.py:3,11` uses it internally. This is the only in-repo caller.
- `docs/api.md:8` lists `userclient.fetch(user_id)` as **stable**. The same file says changes that break a listed name "wait for the next major release".
- The package is at version 2.1.0 (`pyproject.toml`). Its next major release would be 3.0.
- `tests/test_client.py` only covers `build_url` (marked internal). No test touches `fetch`.
- There are no aliases, deprecation helpers or changelog in the repo. `README.md` points to `docs/api.md` as the supported surface.

## What the request leaves undecided

The rename touches a documented public, stable name. A plain rename (changing the definition, export, import in `sync.py` and the docs) would break any external caller of `userclient.fetch`. The repository's own policy says that must wait for a major release. The request doesn't say how to handle this. I can't resolve it from the repo, because I can't see external consumers or the release plans.

Decisions only the requester can make:

1. **Compatibility approach.** The options are:
   - (a) A hard rename now, shipped as 3.0.0 with a breaking-change note.
   - (b) Add `fetch_user` and keep `fetch` as a deprecated alias, and remove `fetch` in the next major release. This is the policy-compliant path in a minor release.
   - (c) An internal-only rename. I think this is unlikely, because the name is public.
2. **If `fetch` stays as an alias:** whether it should emit a `DeprecationWarning`, and when it is removed. The docs table also needs a way to mark `fetch` as deprecated, and it currently has no such status.
3. **Version and release.** If a hard rename is chosen, someone has to decide whether to bump the version to 3.0.0 in this change or leave the bump to the release process.

Points I would settle in the implementation without asking:
- Export `fetch_user` in `__all__`.
- Update `sync.py` and `docs/api.md`.
- Add a test for `fetch_user`, and for the alias if one is kept.
- Keep the `client.fetch_user` module path as the definition site.

OPEN-DECISIONS: 1
