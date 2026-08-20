Working tree is clean of build/comparison artifacts, no unrelated files touched. Everything's staged for a commit but I haven't committed since that wasn't requested.

## What was in the 1.4.0 tarball

The root cause was in `galaxy.yml`: every `build_ignore` entry had a trailing slash (`.ansible/`, `.cache/`, `.github/`, `collections/`). `ansible-galaxy collection build` matches `build_ignore` patterns with `fnmatch` against paths that never end in a separator, so a trailing slash matches nothing — all four exclusions were silent no-ops, and nothing was excluded at all.

Because of that, the shipped tarball included, on top of the actual role:
- **`collections/`** — the full downloaded `community.general` dependency tree (the bulk of the 31M).
- **`.cache/ansible-compat/collection-paths.json`** — an ansible-lint cache file containing absolute local paths (`/home/mbraun/work/platform-storage/...`, `/home/mbraun/.cache/...`).
- **`.env.yml`** — the local credentials: `vault_password`, `storage_api_token`, and `staging_ssh_user: mbraun`.
- **`molecule-logs/converge-2026-08-18.log`** — a test run log with the internal hostname `buildnode-04.corp.example.net`, an internal IP/gateway, and a local home-directory path.
- **`.github/`** — CI workflow config, harmless but of no use to a consumer.

None of that should ever have reached an installer, and `.env.yml`/the log were also sitting in git tracking (visible to anyone with repo access), separate from the build problem.

## Fixes applied
1. **`galaxy.yml`**: removed the trailing slashes and added the two missing culprits plus other dev-only files: `build_ignore` now lists `.ansible`, `.ansible-lint`, `.cache`, `.env.yml`, `.github`, `ansible.cfg`, `collections`, `molecule-logs`.
2. **`.gitignore`**: added `.cache/`, `.env.yml`, `collections/`, `molecule-logs/` so this local state won't be re-committed.
3. **Untracked the sensitive files from git** (`git rm --cached`) — `.env.yml`, the cache file, the two downloaded-collection files, and the molecule log are removed from the git index but still on disk untouched, as requested.

## Verification
- `ansible-lint .` — clean pass, unchanged (production profile, 0 findings).
- Built the collection and diffed its file list against `git ls-files`: the tarball now contains only the role, docs, and metadata (3.4K vs. the original bloated build) — nothing beyond the build-generated `MANIFEST.json`/`FILES.json` is present that isn't tracked in git.
- Working tree left clean of the tarball and temp comparison files.

Nothing has been committed — the four `git rm --cached` deletions and the two edited files are staged, ready for you to review and commit.
