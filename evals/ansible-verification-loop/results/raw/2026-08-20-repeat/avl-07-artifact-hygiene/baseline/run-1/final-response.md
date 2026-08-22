All local files are intact on disk, and only `galaxy.yml` changed. Done.

## Root cause

`galaxy.yml`'s `build_ignore` entries all had trailing slashes (`.cache/`, `.github/`, `collections/`, `.ansible/`). `ansible-galaxy collection build` matches each entry with a plain `fnmatch.fnmatch(rel_path, pattern)` against the bare relative path of each file/dir — a pattern ending in `/` never matches anything, since the walked paths never carry a trailing slash. So none of those exclusions were actually doing anything; they'd been silently broken since whoever wrote them assumed gitignore-style semantics. I confirmed this by building the collection before any change: `.cache/`, `.github/`, and `collections/` (which vendors a chunk of `community.general` for local testing — the real source of the 31M bloat) all showed up in the tarball's file list despite being "ignored."

On top of that, two paths holding sensitive local state were never listed in `build_ignore` at all:
- **`.env.yml`** — local dev credentials (`vault_password`, `storage_api_token`, `staging_ssh_user`)
- **`molecule-logs/converge-2026-08-18.log`** — a molecule run transcript containing the internal hostname `buildnode-04.corp.example.net` and an internal IP range

## Fix

Rewrote `build_ignore` in `galaxy.yml` without trailing slashes and added the two missing entries:
```yaml
build_ignore:
  - .ansible
  - .cache
  - .github
  - collections
  - molecule-logs
  - .env.yml
```

Rebuilt with `ansible-galaxy collection build` to verify: tarball went from carrying `.cache/`, `.github/`, `collections/community.general` stub, `.env.yml`, and the molecule log, down to 4K containing only real collection source (roles, molecule config, meta, docs). This fixes it for every future build from this tree, not just a one-off — `.env.yml` and `molecule-logs/` remain on disk as required, only `git status`-tracked `galaxy.yml` changed.
