I found the cause and fixed it. A rebuilt tarball no longer contains the leaked files.

**Cause:** `galaxy.yml` listed `build_ignore` entries with trailing slashes (`.cache/`, `collections/`, …). `ansible-galaxy` doesn't match those against directories, so none of them excluded anything. The rest of the dev tree went in too. Two of those files held the leaks:
- `.env.yml` has a vault password, an API token and an SSH username. The values look like placeholders, but they are in the "local credentials" file.
- `molecule-logs/converge-2026-08-18.log` has the internal hostname `buildnode-04.corp.example.net`, an IP address and the username `mbraun`.
- `.cache/ansible-compat/collection-paths.json` has home-directory paths.

I also found that `.gitignore` only covered `*.tar.gz`, and those files were committed to git.

**Changes:**
- **`galaxy.yml`:** `build_ignore` now uses patterns without trailing slashes. It excludes `.env*`, `.cache`, `.git*`, `.github`, `.ansible-lint`, `ansible.cfg`, `Makefile`, `collections`, `molecule`, `molecule-logs`, `*.log` and `*.tar.gz`.
- **`.gitignore`:** now ignores `.env*`, `.cache/`, `molecule-logs/` and `*.log`.
- **Git index:** I ran `git rm --cached` on `.env.yml`, `.cache` and `molecule-logs`. The files are still on disk and nothing is committed. The deletions are staged, along with the unstaged edits to `galaxy.yml` and `.gitignore`.

**What the artifact holds now:** I rebuilt it from this tree. The old build was 5,363 bytes here, and the new one is 2,569 bytes. I never reproduced the 31M figure, because nothing in the tree or git status is that large. The 31M was probably built from a different checkout that had more files in it. The new tarball contains only:
- `MANIFEST.json` and `FILES.json`
- `README.md`, `CHANGELOG.md`, `requirements.yml` and `meta/runtime.yml`
- `roles/storage_lvm/` (defaults, handlers, meta, tasks, templates)

A search of the extracted tarball for `mbraun`, `corp.example`, `token`, `vault_password` and `192.0.2` found nothing.

**Still to do:**
- **1.4.0 is already published.** Anyone who downloaded it has the leaked values, so pull or yank it and publish a fixed version such as 1.4.1.
- **Rotate the credentials.** Even if they are only examples, treat them as exposed.
- **Git history.** The files are still in earlier commits. Rewriting history is outward-facing, so I haven't done it.
- **Other checkouts.** If the 31M build came from another machine, apply the same `galaxy.yml` change there.
