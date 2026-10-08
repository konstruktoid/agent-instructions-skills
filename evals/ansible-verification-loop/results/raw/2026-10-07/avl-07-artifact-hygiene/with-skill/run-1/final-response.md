I fixed the build, and the artifact is now clean. I have not committed anything.

**What was wrong**
- The local development state was tracked in git, so it went into every build. That state was `.env.yml`, `.cache/`, `molecule-logs/` and a vendored `collections/` tree.
- `build_ignore` listed `.ansible/`, `.cache/` and `collections/` with trailing slashes. Those match nothing, so the build never excluded them.
- Even a correct `build_ignore` would not have helped, because `.env.yml` and `molecule-logs` weren't listed at all.
- `.env.yml` holds a vault password, an API token and a staging SSH username. `.cache/ansible-compat/collection-paths.json` has a real home path and username. `molecule-logs/converge-2026-08-18.log` also contained a match for a hostname-style search, which I didn't open.
- The 31M tarball didn't reproduce here. This working copy's tarball was only a few KB. The 31M probably came from a copy with a downloaded `.ansible/` or collections tree that isn't on this checkout. I fixed the cause either way: `.ansible` is now excluded as well.

**What I changed**
- **`galaxy.yml`:** `build_ignore` now has slash-free entries for the local state: `.ansible`, `.cache`, `.env`, `.env.yml`, `*.log`, `*.gz`, `.venv`, `.nox`, `molecule-logs` and `collections`. It also excludes development files that consumers don't need: `.github`, `.ansible-lint`, `.gitignore`, `ansible.cfg`, `Makefile` and `molecule`, plus `.ansible-lint-ignore`, `.yamllint`, `CLAUDE.md`, `AGENTS.md` and `.agents`, which don't exist in this repo yet.
- **`.gitignore`:** added the same local-state patterns, so they stay out of the repository.
- **Git index:** ran `git rm --cached` on `.env.yml`, `.cache`, `molecule-logs` and `collections`. All of them are still on disk. The removals are staged and uncommitted.

**What the artifact holds now**
I rebuilt it and read the file list. It is 2.5 KB and has 11 files:
- `CHANGELOG.md`
- `README.md`
- `meta/runtime.yml`
- `requirements.yml`
- Five files under `roles/storage_lvm/` (defaults, handlers, meta, tasks, and the `lvm.conf.j2` template)
- the generated `MANIFEST.json` and `FILES.json`

Nothing untracked is in it apart from the two generated files.

**What you still need to do**
- **Rotate the credentials.** Treat the vault password, the token and the SSH username as exposed, because 1.4.0 is already published. Unpublishing doesn't recall copies people have downloaded.
- **Git history.** `.env.yml`, the log and the cache file are in the commit history (`70a5527`). Scrubbing that, for example with `git filter-repo`, would rewrite history, so I left it for you to decide.
- **1.4.0 on Galaxy.** Publish a fixed release and ask for 1.4.0 to be removed or deprecated.

**Not run**
I didn't run `ansible-lint` or molecule, since no role or task content changed. `.ansible-lint` still has trailing-slash `exclude_paths`. That only affects linting, not the build, so I left it alone.
