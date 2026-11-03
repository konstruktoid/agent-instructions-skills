The build now excludes the local files, and a fresh build comes out at 2.5 KB. I haven't rebuilt or republished 1.4.0 itself.

**What was wrong**
- The `build_ignore` entries in `galaxy.yml` had trailing slashes (`.cache/`, `collections/`, `.github/`). The Ansible Galaxy build doesn't match patterns written that way, so none of them worked.
- Everything not otherwise excluded went into the tarball, including `.env.yml` and `molecule-logs/converge-2026-08-18.log`.
- `.env.yml` has local credentials (a vault password, an API token and an SSH user). The log has the internal hostname `buildnode-04.corp.example.net`, the user `mbraun` and local paths.
- Those files were also tracked in git, so a build from a git checkout would pick them up too.
- I couldn't find where the 31M came from. Nothing in the tree is larger than 100K, so I think the 1.4.0 build had something bulky that isn't here now (for example a `.ansible/` directory or an older `.tar.gz`). The new patterns exclude both of those.

**What I changed**
- **`galaxy.yml`:** the `build_ignore` entries now work. The list covers `.git`, `.github`, `.cache`, `.ansible`, `.env*`, `collections`, `molecule`, `molecule-logs`, `*.log`, `*.tar.gz`, `Makefile`, `ansible.cfg`, `.ansible-lint` and `.gitignore`.
- **`.gitignore`:** added `.env*`, `molecule-logs/`, `.cache/`, `.ansible/` and `*.log`.
- **Git index:** ran `git rm --cached` on `.env.yml`, `molecule-logs/` and `.cache/`, so they are no longer tracked. All three are still on disk. The removal is staged but not committed.

**What the artifact holds now**
- `MANIFEST.json`, `FILES.json`, `README.md`, `CHANGELOG.md`, `requirements.yml` and `meta/runtime.yml`.
- The `roles/storage_lvm` role: defaults, handlers, meta, tasks and the template.
- I extracted it and searched for `mbraun`, `corp.example`, `vault_password` and `api_token`, and found nothing.

**Still to do**
- The credentials and hostname are still in git history, and the already-published 1.4.0 still contains them. Treat the vault password, API token and hostname as exposed. Rotate them, even though the values look like placeholders.
- Publish the fixed tarball as a new version and pull or yank 1.4.0 if Galaxy allows it. I didn't do either.
