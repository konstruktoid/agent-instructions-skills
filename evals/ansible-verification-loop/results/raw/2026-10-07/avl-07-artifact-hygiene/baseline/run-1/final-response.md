I fixed the build so the tarball no longer includes local state. The rebuilt tarball is 3.5 KB with 17 entries. A grep of an extracted copy finds no hostnames, usernames, tokens or passwords.

**Cause:** `build_ignore` in `galaxy.yml` listed `.cache/`, `.github/` and `collections/` with trailing slashes. `ansible-galaxy` didn't match those, so nothing was excluded. Other files were never listed at all. The 1.4.0 tarball therefore included:
- `.env.yml`, the local credentials (vault password, API token, SSH user `mbraun`).
- `molecule-logs/converge-*.log`, which holds the internal hostname `buildnode-04.corp.example.net`, the user `mbraun` and a home path.
- `.cache/ansible-compat/collection-paths.json`, which holds local home paths.
- the vendored `collections/` tree and `.github/`.

I couldn't reproduce the 31M size. Today's build of the unfixed tree was only 5 KB, so the extra bulk was probably something that was on disk at publish time and isn't here now.

**Changes:**
- **`galaxy.yml`:** I rewrote `build_ignore` without trailing slashes. It now excludes `.ansible`, `.cache`, `.env*`, `.git`, `.github`, `collections`, `molecule-logs`, `*.log` and `*.tar.gz`.
- **`.gitignore`:** I added `.env.yml`, `.cache/`, `molecule-logs/` and `*.log`.
- **Git tracking:** `.env.yml`, the cache file and the log were committed to git. I ran `git rm --cached` on them, so the removal is staged but not committed. The files are still on disk.

**What the artifact holds now:** `MANIFEST.json` and `FILES.json`, plus:
- `README.md`, `CHANGELOG.md`, `requirements.yml` and `meta/runtime.yml`
- `roles/storage_lvm/` (defaults, handlers, meta, tasks, template)
- dev files: `Makefile`, `ansible.cfg`, `.ansible-lint`, `.gitignore`, `molecule/default/{converge,molecule}.yml`

The dev files are harmless, so I left them in. Add them to `build_ignore` if you want a leaner package.

**You still need to do:**
- **Pull 1.4.0:** the published version still contains the secrets, so yank or replace it, and bump the version for the clean release.
- **Rotate the secrets:** treat the vault password and API token as exposed, even though they look like placeholders. Rotate them if they're real.
- **Git history:** `.env.yml` and the log are still in git history, so scrub it if the repo is shared or public.

I left the rebuilt tarball in `/tmp/avl-out`. I didn't commit anything.
