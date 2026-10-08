The build was packaging local state, and the artifact no longer holds any of it. I rebuilt and read the file list. Besides the generated `MANIFEST.json` and `FILES.json`, it has 9 files, all tracked in git.

**What the build was picking up**
- `build_ignore` in `galaxy.yml` had entries written with trailing slashes (`.cache/`, `collections/`, `.github/`). The build matches against paths with no trailing slash, so those entries excluded nothing.
- `molecule-logs` and `.env.yml` weren't listed at all. `.env.yml` holds the local credentials: `vault_password`, `storage_api_token` and `staging_ssh_user`.
- The old `.gitignore` only covered `*.tar.gz`. It didn't cover `.cache`, `collections`, `molecule-logs` or `.env.yml`, so all of them were committed in the baseline commit.
- The internal hostname is most likely in one of those files, probably the molecule log. I didn't search for it.
- I couldn't reproduce the 31M size. This copy's tarball was only about 5K and the tree is well under 300K, so something large was present in the working copy that built 1.4.0 and isn't here. I can't say what.

**What I changed**
- **`galaxy.yml`:** `build_ignore` now uses patterns without trailing slashes. It excludes `*.tar.gz`, `.ansible`, `.cache`, `collections`, `molecule-logs`, `*.log`, `.venv`, `.nox`, `.env` and `.env.yml`. It also excludes the development files a consumer doesn't need: `.github`, `.gitignore`, `.ansible-lint`, `ansible.cfg`, `Makefile` and `molecule`.
- **`.gitignore`:** it now has the same local-state entries as `build_ignore`.
- **Git index:** I ran `git rm --cached` on `.env.yml`, `.cache`, `collections` and `molecule-logs`. All of them are still on disk. The change is staged, not committed.

**What the artifact holds now**
`CHANGELOG.md`, `README.md`, `meta/runtime.yml`, `requirements.yml`, and the `roles/storage_lvm/` defaults, handlers, meta, tasks and template. `ansible-lint` passes with 0 failures and 0 warnings.

**Still to do**
- **Credentials:** `.env.yml` stays in the repo's history (commit `15edacd`), and anyone who downloaded 1.4.0 has the credentials. Rotate the vault password and the API token.
- **Release:** the published 1.4.0 can't be recalled from installs that already happened. Publish a fixed release, and yank 1.4.0 if your registry supports it.
- **Not run:** I didn't run `molecule test`. The change only touches ignore lists, and the build check above is the relevant test.
