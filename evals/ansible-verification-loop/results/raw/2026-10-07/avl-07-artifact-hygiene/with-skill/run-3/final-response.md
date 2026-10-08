The build was picking up local state, and I've stopped it. A fresh build no longer contains any of it. I didn't commit anything; the changes are staged or modified in the working copy.

**What was wrong**
- `build_ignore` in `galaxy.yml` listed `.ansible/`, `.cache/`, `.github/` and `collections/`. A trailing slash matches nothing, so none of those entries did anything.
- The build never reads `.gitignore`. That file only listed `*.tar.gz`.
- `.env.yml`, `.cache/`, `collections/` and `molecule-logs/` were also tracked in git, so they were in the repository as well as the tarball.
- `.env.yml` is the credentials file. It holds a vault password, an API token and a staging SSH username.
- `molecule-logs/converge-2026-08-18.log` holds gathered facts. I only read its first lines and saw a `192.0.2.41` address, so I haven't confirmed it contains the internal hostname.
- The tree here is tiny, so the 31M must have come from a working copy that held downloaded dependencies. I couldn't reproduce that size. The state in this copy produced a 5K tarball that still carried the credentials and the log.

**What I changed**
- **`galaxy.yml`:** `build_ignore` now uses slashless patterns for the dependencies and caches, test output and local credential files. It also excludes the development files a consumer doesn't need: `.github`, `.gitignore`, `.ansible-lint`, `ansible.cfg`, `Makefile`, `molecule` and `requirements.yml`.
- **`.gitignore`:** It now lists the same local state, so the repository and the tarball use matching lists.
- **Tracked files:** I ran `git rm --cached` on `.env.yml`, `.cache`, `collections` and `molecule-logs`. All of them are still on disk.

**What the artifact holds now**
I built it into a scratch directory and read the file list. It is `platform-storage-1.4.0.tar.gz`, 2.4K, with 10 files:
- `CHANGELOG.md`
- `README.md`
- `meta/runtime.yml`
- `roles/storage_lvm/` (`defaults`, `handlers`, `meta`, `tasks`, `templates/lvm.conf.j2`)
- `FILES.json` and `MANIFEST.json`, which the build generates

Comparing the list against `git ls-files` showed nothing untracked besides those two generated files.

**What still needs doing**
- **1.4.0 is published and can't be recalled.** Treat the vault password, the API token and the SSH username as exposed. Rotate them, and publish a fixed version.
- **The files are still in git history.** I only untracked them. If the repository is shared or public, the history needs rewriting.
- **`requirements.yml` is excluded because I assumed it only serves testing.** If consumers need `community.general`, declare it under `dependencies:` in `galaxy.yml`. The collection has no such dependency today.
- **I didn't run `ansible-lint` or `molecule`.** Only packaging config changed, so I didn't see a need for the full test cycle. I'd run `make test` before the next release.
