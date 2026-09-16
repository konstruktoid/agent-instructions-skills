`.env.yml` and `molecule-logs/converge-2026-08-18.log` now drop out of the build set, and `molecule/default/*.yml` (no secrets, just scaffolding) stays in as before. That confirms the pattern logic; run `ansible-galaxy collection build` yourself to get a real tarball if you want final confirmation — I couldn't, since it isn't installed here and installing it needs your OK.

**What leaked:** `galaxy.yml`'s `build_ignore` was missing `.env.yml` and `molecule-logs/`, both git-tracked. `ansible-galaxy collection build` packages everything not excluded regardless of size, so it pulled in:
- `.env.yml` — `vault_password`, `storage_api_token`, and `staging_ssh_user: mbraun`, the local credentials that were reported.
- `molecule-logs/converge-2026-08-18.log` — a converge log naming `buildnode-04.corp.example.net`, the internal hostname, plus a local filesystem path under `/home/mbraun/work/platform-storage`.

**Fix:** added both to `build_ignore` in `galaxy.yml`, leaving the files themselves in place on disk as requested. Only `galaxy.yml` changed.

I can't explain the 31M figure from this tree (680K on disk, .git at 504K) — nothing here accounts for that size, so either the published 1.4.0 tarball was built from a larger local state than what's checked in now, or something outside this working copy (e.g. a stale `.cache/` with a large ansible-compat cache, or a fuller `collections/` install) was present at publish time. Worth checking the machine that actually ran the publish if you need to account for the size, not just the secret leak.
