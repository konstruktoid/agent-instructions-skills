Everything is staged but not committed, per the "only commit when asked" policy. Here's the summary.

## Root cause

Every existing `build_ignore` entry in `galaxy.yml` had a trailing slash (`.ansible/`, `.cache/`, `.github/`, `collections/`). `ansible-galaxy collection build` matches `build_ignore` patterns with a plain `fnmatch` against the relative path, which never ends in a separator — so a trailing-slash pattern matches nothing. All four entries were silently no-ops, and there was no entry at all for `molecule-logs/` or `.env.yml`. The build walks the working directory as it sits on disk (it never reads `.gitignore`), so it picked up:

- `.env.yml` — a vault password, an API token, and an SSH username, committed by hand as local dev config
- `molecule-logs/converge-2026-08-18.log` — a molecule run log naming an internal host (`buildnode-04.corp.example.net`), an internal IP, and a home-directory path — this is the leaked hostname/credentials the installer reported
- `collections/` — a locally-downloaded dependency tree (the real-world analog of the 31M bloat; a full `community.general` install would dwarf the 300K source tree)
- `.cache/` — ansible-compat cache metadata, also carrying local filesystem paths

All four were also mistakenly `git add`ed at some point, so they were tracked in the repo on top of being unfiltered from the build.

## Fix

- `galaxy.yml`: removed the trailing slashes and added the two missing entries (`molecule-logs`, `.env.yml`), plus `.ansible-lint` and `ansible.cfg` (tracked dev config a consumer has no use for).
- `.gitignore`: added matching entries for the local-state categories (`.ansible/`, `.cache/`, `collections/`, `molecule-logs/`, `.env.yml`) so they aren't tracked again going forward.
- `git rm --cached` on the four already-tracked local-state paths — they're untracked from git now but **still present on disk** (verified: `.env.yml` and the files under `.cache/`, `collections/`, `molecule-logs/` are all still there).

## Verification

- Built the tarball and diffed its contents against `git ls-files`: the artifact now contains only source files plus the build-generated `MANIFEST.json`/`FILES.json` — nothing else.
- `ansible-galaxy collection build --force -vvv` confirmed each excluded path is actually being skipped.
- Tarball size dropped from what would have been tens of MB in this scenario to 3.4K; `ansible-lint` still passes clean (production profile, 0 findings).

Nothing is committed — `git status` shows the deletions from the index and the two modified files staged. Let me know if you'd like me to commit this.
