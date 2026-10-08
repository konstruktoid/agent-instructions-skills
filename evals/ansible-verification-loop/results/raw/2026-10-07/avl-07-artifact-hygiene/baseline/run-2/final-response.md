The build no longer picks up the local files, and the rebuilt 1.4.0 tarball holds only the collection content. I checked this by running `ansible-galaxy collection build` again and listing the archive.

**Cause:** `galaxy.yml` listed its `build_ignore` entries with trailing slashes (`.cache/`, `collections/`, and so on). Those patterns don't match anything, so the build excluded nothing and packed the whole working directory. That included:
- `.env.yml`, which holds the vault password, API token and staging SSH user.
- `molecule-logs/converge-2026-08-18.log`, which holds the internal hostname `buildnode-04.corp.example.net` and a username.
- `.cache/`, `collections/` (a vendored copy of `community.general`), `.github/`, `molecule/` and other dev files.

**Changes:**
- **`galaxy.yml`:** I rewrote `build_ignore` without the trailing slashes. It now excludes `.ansible`, `.cache`, `.github`, `.git`, `.gitignore`, `.ansible-lint`, `.env*`, `*.log`, `*.tar.gz`, `ansible.cfg`, `collections`, `Makefile`, `molecule`, `molecule-logs` and `requirements.yml`.
- **`.gitignore`:** I added `.env*`, `.cache/` and `molecule-logs/`.
- **Git index:** I ran `git rm --cached` on `.env.yml`, `.cache` and `molecule-logs`. They had been committed, so they are staged for removal from git. Nothing is committed.
- **On disk:** All those files are still there.

**What the new tarball holds** (2.4 KB, 10 files):
- `MANIFEST.json` and `FILES.json`
- `README.md` and `CHANGELOG.md`
- `meta/runtime.yml`
- `roles/storage_lvm/` (defaults, handlers, meta, tasks, and the `lvm.conf.j2` template)

I searched the remaining sources for `mbraun` and `corp.example`. They appear only in the three local files above, none of which is in the new tarball.

**Things for you to do:**
- **Don't ship with the old 1.4.0:** It is already published with the leaked content, and I did not touch that. Publish a fixed version, such as 1.4.1, and pull or deprecate 1.4.0 on Galaxy.
- **Rotate the leaked secrets:** The values in `.env.yml` look like placeholders (`...-not-in-use`). If any real values ever sat in that file, rotate them.
- **Git history:** The files are still in history, so anyone with repo access can read them. Scrub the history if that matters to you.
- **Size mismatch:** I couldn't reproduce the 31M. This checkout builds to about 20 KB with the old config. The published build was probably made somewhere with extra untracked content, such as a `.ansible/` directory. `.ansible` is now excluded, but check the machine that did the publish.
