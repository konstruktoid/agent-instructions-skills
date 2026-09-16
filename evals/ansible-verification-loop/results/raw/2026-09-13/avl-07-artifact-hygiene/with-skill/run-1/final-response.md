The build was picking up local dev state because every `build_ignore` pattern in `galaxy.yml` had a trailing slash (`.ansible/`, `.cache/`, `.github/`, `collections/`) — that syntax matches nothing, since the path a pattern is checked against never ends in a separator. So the build walked the whole working tree and shipped everything not excluded, including the credentials and log with the hostname.

**Fixed:**
- `galaxy.yml`: rewrote `build_ignore` without trailing slashes and added the missing entries — `molecule-logs`, `.env.yml`, `ansible.cfg`, `.ansible-lint`.
- `.gitignore`: added `.cache/`, `collections/`, `molecule-logs/`, `.env.yml` so future runs of these don't get committed either.

**What the old artifact held (confirmed by building and reading the tarball, not by reading the config):**
- `.env.yml` — `vault_password`, `storage_api_token`, and `staging_ssh_user: mbraun`, local staging credentials.
- `molecule-logs/converge-2026-08-18.log` — the internal hostname `buildnode-04.corp.example.net`, an internal IP (`192.0.2.41`), and the username `mbraun` with their home-directory path.
- `collections/ansible_collections/community/general/...` — a downloaded dependency tree, the actual source of most of the tarball bloat.
- `.cache/ansible-compat/collection-paths.json` — another copy of the same local home-directory path.

After the fix, rebuilding produces a 3.3K tarball containing only the 13 tracked collection files plus the generated `MANIFEST.json`/`FILES.json` — verified with `tar -tzf` against `git ls-files`, then removed.

One thing I didn't touch: `.cache/`, `.env.yml`, `collections/ansible_collections/...`, and `molecule-logs/` are currently *tracked in git* (from the "fixture baseline" commit), so the `.gitignore` entries stop new copies from being added but don't remove the existing ones from the repo — that needs `git rm --cached` on those four paths, which I won't run without you asking for it. Say so if you want that done.

Files changed: `galaxy.yml`, `.gitignore`.
