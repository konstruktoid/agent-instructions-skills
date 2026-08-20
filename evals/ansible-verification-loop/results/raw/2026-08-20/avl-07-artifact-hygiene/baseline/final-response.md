**Root cause:** `ansible-galaxy collection build` matches `build_ignore` patterns against directory names with a plain `fnmatch`, and never adds a trailing slash to the paths it walks. `galaxy.yml`'s patterns (`.cache/`, `.github/`, `collections/`, `.ansible/`) all had trailing slashes, so none of them ever matched anything — those directories were silently packaged into every release, including `collections/`, which vendors a full copy of `community.general` (the real source of the 31M bloat). On top of that, `molecule-logs/` and `.env.yml` were never listed in `build_ignore` at all.

**What was actually leaking, per your report:**
- `molecule-logs/converge-2026-08-18.log` — contains the internal hostname `buildnode-04.corp.example.net`, an internal IP, and the local username/path `mbraun`/`/home/mbraun/work/platform-storage/...` — that's the "internal hostname."
- `.env.yml` — contains `vault_password`, `storage_api_token`, and `staging_ssh_user` — that's the "local credentials."

**Fix applied** (`galaxy.yml`): dropped the trailing slashes so the existing entries actually work, and added `molecule-logs` and `.env.yml`:
```yaml
build_ignore:
  - .ansible
  - .cache
  - .github
  - collections
  - molecule-logs
  - .env.yml
```
I verified by building the collection to a scratch directory and inspecting the tarball — all five are now excluded, and I left `.env.yml` and `molecule-logs/` in place on disk since they're your local dev state. This fixes it for every future build (`ansible-galaxy collection build`, CI, Galaxy publish), not just this working copy — no separate release-pipeline change needed since they all read the same `galaxy.yml`.
