I've fixed the build in this working copy and checked it by rebuilding. Nothing is committed yet.

**Cause:** `build_ignore` in `galaxy.yml` listed `.cache/` and `collections/` with trailing slashes, which match nothing, so those two directories shipped. It had no entries at all for `.env.yml` or `molecule-logs`. `ansible-galaxy collection build` ignores `.gitignore`, and these four paths were also tracked in git (the baseline commit includes them), so they were doubly exposed.

Four things made it into the 1.4.0 tarball that shouldn't have:
- `.env.yml` (local credentials: a vault password, an API token and an SSH user)
- `molecule-logs/` (where the internal hostname most likely came from; I didn't check the log's contents)
- `.cache/`
- a vendored `collections/ansible_collections/community/general`

The development files `.github`, `ansible.cfg`, `Makefile`, `.ansible-lint`, `.gitignore` and `molecule/` also shipped.

**Changes:**
- `galaxy.yml`: `build_ignore` now has a slash-free entry for each local-state path. It also excludes `*.log`, `*.tar.gz`, `.venv` and the development files above.
- `.gitignore`: it only had `*.tar.gz`. I added the local-state paths (`.ansible`, `.cache`, `.env`, `.env.yml`, `.venv`, `.nox`, `collections`, `molecule-logs`, `*.log`).
- I ran `git rm --cached` on `.env.yml`, `.cache`, `collections` and `molecule-logs`. The files are still on disk; the removals are staged but not committed.

**What the artifact holds now:** 11 files, 2.5 KB, built to a scratch directory. They are `CHANGELOG.md`, `README.md`, `meta/runtime.yml`, `requirements.yml`, the `storage_lvm` role (defaults, handlers, meta, tasks and the `lvm.conf.j2` template), and the generated `FILES.json` and `MANIFEST.json`. A comparison against `git ls-files` shows nothing untracked beyond those two generated files.

`ansible-lint .` passes with 0 failures and 0 warnings. I did not run `molecule test`.

**For you to do:**
- **Rotate the credentials.** The vault password and API token are in the published 1.4.0 and in git history (commit `384194c`), and I didn't rewrite history. Removing a version from Galaxy doesn't recall copies already downloaded. Yank 1.4.0 and republish a corrected release.
- **Commit the change.** I haven't committed. The next build only comes out clean once the staged removals and the `galaxy.yml` and `.gitignore` edits are in your tree.
- **Check the artifact size.** The tarball I built is 5 KB before the fix, not 31 MB, so this copy doesn't reproduce the 31 MB. The 31 MB build probably had a populated `.ansible/` directory or downloaded dependencies on the machine that published it. I added `.ansible` to both ignore lists, and the pattern is slash-free, so it will match. It's worth building once on that machine and reading the file list.
