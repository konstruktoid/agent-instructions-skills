The build was packaging local development state, and I've stopped it. The rebuilt 1.4.0 artifact is now 11 files, about 2.5K.

**Cause**
- `build_ignore` listed `.ansible/`, `.cache/`, `.github/` and `collections/`. Each had a trailing slash, which matches nothing, so those entries did nothing.
- `.gitignore` held only `*.tar.gz`, so the local state was also tracked in git. It was in the repo as well as in the tarball.
- Nothing in this copy is large, so I couldn't reproduce the 31M. The old build here came to about 5K. The 31M probably came from a populated `collections/` or `.ansible/` on the machine that published it.

**What shipped before**
- `.env.yml`: a vault password, an API token and an SSH username.
- `molecule-logs/converge-*.log`: gathered facts with addresses and an FQDN.
- `.cache/`.
- A vendored `collections/ansible_collections/community/general`.
- Dev files: `.github`, `.ansible-lint`, `ansible.cfg`, `Makefile` and `molecule/`.

**Changes**
- **`galaxy.yml`:** `build_ignore` is rewritten without trailing slashes. It covers the local state above, `.venv`, `.nox`, `*.log`, `*.gz` and the dev files listed above, plus `.gitignore`.
- **`.gitignore`:** it now lists the same local-state patterns.
- **Untracked, not deleted:** I ran `git rm --cached` on `.env.yml`, `.cache`, `collections` and `molecule-logs`. They're still on disk. The removals are staged, not committed.

**What the artifact holds now**
- `CHANGELOG.md`, `README.md`, `meta/runtime.yml` and `requirements.yml`.
- The `roles/storage_lvm` files: defaults, handlers, meta, tasks and the `lvm.conf.j2` template.
- `MANIFEST.json` and `FILES.json`, which the build generates.
- I checked this by building and reading the file list. Comparing it against `git ls-files` shows only the two generated files as untracked.
- `ansible-lint .` passes with 0 failures and 0 warnings. I didn't run the molecule suite, since the change doesn't touch role behavior.

**What you need to do**
- **Rotate the credentials.** The vault password and token were published in 1.4.0 and the history still holds them. Deleting the file doesn't recall copies already downloaded. `staging_ssh_user` and the internal hostname were exposed the same way.
- **Pull the published 1.4.0** from Galaxy and republish a fixed version.
- **Purge the history if you need to.** The baseline commit still contains these files. Purging them means rewriting history, for example with `git filter-repo`. I haven't done that or committed anything. Tell me if you want either.
- **Check `requirements.yml`.** I left it in the artifact. Remove it from the build if it only lists dev dependencies.
