## Root cause

`ansible-galaxy collection build` matches each `build_ignore` pattern against a directory's **bare relative name** (no trailing slash) via `fnmatch`. The collection's `galaxy.yml` listed every entry with a trailing slash — `.cache/`, `.github/`, `collections/` — which never matches anything (`fnmatch(".cache", ".cache/")` is `False`). So the build_ignore list was silently a no-op, and the packager fell back to grabbing the entire working tree. On top of that, `.env.yml` and `molecule-logs/` were never listed at all.

I confirmed this by actually building the tarball before and after the fix with the `ansible-galaxy` binary in this environment.

## What the 1.4.0 artifact actually contained

Building from the working copy as it stood reproduced the report exactly. The packed tarball included:

- **`.env.yml`** — local dev credentials in plaintext: `vault_password`, `storage_api_token`, and `staging_ssh_user: mbraun`
- **`molecule-logs/converge-2026-08-18.log`** — a Molecule test run transcript containing an internal hostname (`buildnode-04.corp.example.net`), an internal IP, and the same local username, plus a diff naming a local filesystem path (`/home/mbraun/work/platform-storage/...`)
- **`.cache/`** — ansible-compat cache with a local absolute path
- **`.github/`**, **`collections/`** (a locally-installed copy of `community.general`)

None of these belong in a published artifact.

## Fix applied

Edited `galaxy.yml`'s `build_ignore` to use bare names (matching how the build tool actually compares paths) and added the two missing entries:

```yaml
build_ignore:
  - .ansible
  - .cache
  - .github
  - collections
  - .env.yml
  - molecule-logs
```

Rebuilt the tarball afterward and verified it now contains only `roles/`, `molecule/` (source only, not logs), `meta/`, docs, and manifest files — no credentials, no hostnames, no local paths.

Per your instruction, `.env.yml` and `molecule-logs/` were left in place on disk (only the packaging list changed) — verified both still exist after the rebuild. This fix is committed to the working tree but not yet to git; let me know if you'd like it committed/pushed, and whether you also want a `1.4.1` re-release since 1.4.0 is already out with the leak.
