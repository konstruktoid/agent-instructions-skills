The leak is fixed. A rebuilt 1.4.0 tarball is 2.7 KB, and none of the local files are in it.

**What the build was picking up**
- **Directory patterns:** `build_ignore` in `galaxy.yml` listed `.cache/`, `.github/` and `collections/` with trailing slashes. `ansible-galaxy` doesn't match patterns written that way. I confirmed this with a test build, where all three directories still went into the tarball.
- **Missing entries:** `.env.yml` and `molecule-logs/` weren't listed at all.
- **`.env.yml`:** it holds local credentials: a vault password, an API token and the SSH user `mbraun`. The values look like placeholders.
- **`molecule-logs/converge-2026-08-18.log`:** it contains the internal hostname `buildnode-04.corp.example.net`, an internal IP and the user's home path.
- **`.cache/ansible-compat/collection-paths.json`:** it also holds the home path.
- **`collections/`:** this is a vendored copy of `community/general` that doesn't belong in a published collection.

**Changes**
- **`galaxy.yml`:** I removed the trailing slashes from the existing patterns. I also added `.env*`, `molecule-logs`, `molecule`, `*.log`, `*.tar.gz`, `Makefile`, `.ansible-lint` and `ansible.cfg`.
- **`.gitignore`:** I added `.env*`, `molecule-logs/`, `.cache/` and `*.log`.
- **Git index:** all three paths were tracked in git, so I ran `git rm --cached` on them. They are still on disk, and I haven't committed anything.

**What the artifact holds** (built to `/tmp/out/platform-storage-1.4.0.tar.gz`, outside the repo)
- `MANIFEST.json`, `FILES.json`, `README.md`, `CHANGELOG.md`, `.gitignore`, `requirements.yml` and `meta/runtime.yml`
- the `roles/storage_lvm` role: defaults, handlers, meta, tasks and the `lvm.conf.j2` template

I searched the tarball contents for `buildnode`, `mbraun`, `token` and `vault_password` and found nothing.

**Things you should know**
- **Already published:** the published 1.4.0 still contains the leaked data. Treat the staging credentials as exposed and rotate them even though the values look like placeholders. Pull or replace that release and publish a new version.
- **Git history:** `.env.yml` and the log are still in earlier commits. If this repo is shared, they'd need a history rewrite to remove them, which I haven't done.
- **31M vs 2.7 KB:** I couldn't reproduce the 31M size, because this working copy is only about 680K in total. The published build must have included something larger that isn't in this copy.
