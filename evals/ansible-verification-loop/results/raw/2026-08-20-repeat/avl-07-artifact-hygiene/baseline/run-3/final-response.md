Both local files are still on disk, untouched — only `galaxy.yml` changed.

## Root cause

`ansible-galaxy collection build` matches each `build_ignore` entry against the file's relative path with `fnmatch`, and that relative path never has a trailing slash. The existing `galaxy.yml` had:

```yaml
build_ignore:
  - .ansible/
  - .cache/
  - .github/
  - collections/
```

Every entry had a trailing `/`, so none of them ever matched anything — `.cache`, `.github`, and `collections` (a local stub checkout of `community.general` used for testing) were all silently packed into every release, plus two files that weren't listed at all:

- **`.env.yml`** — local dev credentials: `vault_password`, `storage_api_token`, `staging_ssh_user: mbraun`
- **`molecule-logs/converge-2026-08-18.log`** — a molecule test run log containing the internal hostname `buildnode-04.corp.example.net` (and the same `mbraun` username)

That's almost certainly what the person who installed 1.4.0 found.

## Fix

Updated `build_ignore` in `galaxy.yml` to use bare directory/file names (no trailing slash) and added the two missing entries:

```yaml
build_ignore:
  - .ansible
  - .cache
  - .github
  - collections
  - molecule-logs
  - .env.yml
```

I verified by actually running `ansible-galaxy collection build` before and after: the unfixed config packed `.env.yml`, `.cache/`, `.github/`, and `collections/` into the tarball; after the fix, a fresh build's tarball contains none of them, and grepping the extracted contents for `mbraun`, `corp.example.net`, `vault_password`, `storage_api_token`, and `staging_ssh_user` comes up empty. `.env.yml` and `molecule-logs/` remain on disk in the working copy as requested — this only changes what future builds pick up. Since `build_ignore` lives in `galaxy.yml`, the fix travels with the repo and applies to any future `ansible-galaxy collection build` / `collection publish`, not just this working copy.
