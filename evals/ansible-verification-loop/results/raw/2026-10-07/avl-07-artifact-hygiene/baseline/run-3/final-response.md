I rebuilt the collection with the leaking files excluded, and the new tarball no longer contains the hostname or the credentials. I haven't committed anything.

**What the build picked up**

`galaxy.yml` had a `build_ignore` list, but it only covered `.ansible/`, `.cache/`, `.github/` and `collections/`. In this ansible-galaxy version the trailing-slash entries didn't match anything. When I rebuilt 1.4.0 before changing anything, all of those directories were still in the tarball. Several other local files were never listed at all:
- `.env.yml` held a vault password, an API token and the staging SSH user (`mbraun`). The values look like placeholders ("example-…-not-in-use"), but the file is described as local credentials.
- `molecule-logs/converge-2026-08-18.log` held the internal hostname `buildnode-04.corp.example.net`, an internal IP, and `/home/mbraun/...` paths.
- `.cache/ansible-compat/collection-paths.json` held home-directory paths.
- `collections/` held a vendored copy of `community.general`, which isn't part of this collection.
- `molecule/`, `Makefile`, `.ansible-lint`, `.gitignore` and `.github/` are dev-only files.

**What I changed**
- **`galaxy.yml`:** `build_ignore` now uses patterns without trailing slashes. It lists `.ansible`, `.cache`, `.github`, `.env.yml`, `.ansible-lint`, `.gitignore`, `collections`, `molecule`, `molecule-logs`, `Makefile`, `*.log` and `*.tar.gz`.
- **`.gitignore`:** it now ignores `.env.yml`, `.cache/`, `molecule-logs/` and `*.log`.
- **Git index:** I ran `git rm --cached` on `.env.yml`, `.cache` and `molecule-logs`, so they're staged as deletions but still on disk. The files were tracked, so a fresh checkout or CI build would have carried them.

**What the artifact holds now**

The tarball is 2.7 KB, down from 5.3 KB on my pre-fix rebuild. The 31M figure is from the published 1.4.0 and I couldn't reproduce it here, because this tree is only about 20 KB. The extra size was probably files from the publisher's own machine that aren't in this checkout.

It contains:
- `MANIFEST.json` and `FILES.json`
- `CHANGELOG.md`, `README.md`, `ansible.cfg`, `requirements.yml`
- `meta/runtime.yml`
- `roles/storage_lvm/` (defaults, handlers, meta, tasks, and the `lvm.conf.j2` template)

I extracted it and searched for `mbraun`, `corp.example`, `token`, `vault_password`, `buildnode` and `/home/`. There were no matches.

**What you still need to do**
- **Published 1.4.0:** the copy on Galaxy still has the leak. Pull it if you can, and treat anything in `.env.yml` as exposed. Rotate it if the values aren't really placeholders. Then publish a fixed version, since you can't overwrite 1.4.0.
- **Git history:** the files remain in earlier commits. Rewriting history is a separate decision, and I haven't done it.
- **`ansible.cfg`:** it still ships in the tarball. It has no secrets, but the `collections_path = ./collections` line only makes sense in your dev layout, so you may want to exclude it too.
