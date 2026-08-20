## Root cause

`galaxy.yml`'s `build_ignore` list had every entry written with a trailing slash (`.ansible/`, `.cache/`, `.github/`, `collections/`). `ansible-galaxy collection build` matches `build_ignore` patterns with `fnmatch` against paths that never end in a separator — so a trailing slash matches nothing, and the whole list was a no-op. The build doesn't consult `.gitignore` either; it just walks the working tree and ships anything not excluded.

The artifact your user downloaded therefore contained:
- **`collections/`** — the `community.general` dependency tree pulled in by `requirements.yml` (this is what balloons the tarball; in this repo it's small, but at full size it's the dominant contributor)
- **`molecule-logs/converge-2026-08-18.log`** — a captured test run, including the gathered-facts hostname `buildnode-04.corp.example.net` and the local user `mbraun` — this is the "internal hostname" your user saw
- **`.env.yml`** — `vault_password`, `storage_api_token`, `staging_ssh_user` — this is the "local credentials" your user saw
- **`.cache/`** — ansible-compat's local cache

All four of these were also mistakenly committed to git, which is a separate but related problem — they showed up in `git ls-files` even though nothing in `.gitignore` covered them.

## Fix

- **`galaxy.yml`**: rewrote `build_ignore` without trailing slashes, and added `molecule-logs`, `.env.yml`, `ansible.cfg`, `.ansible-lint`, and `*.log` (tracked dev files a consumer has no use for, plus the local-state files that were leaking).
- **`.gitignore`**: added `collections/`, `.cache/`, `molecule-logs/`, `*.log`, `.env.yml` so this local state stops entering the repo in the first place.
- **`git rm --cached`** on the four already-committed local-state paths — untracked from git, left untouched on disk (confirmed present after).

## Verification

- `ansible-lint .` — clean, 0 failures/warnings, same as baseline.
- Built the collection with `-vvv` and confirmed each file was explicitly logged as skipped.
- Diffed the built tarball's file list against `git ls-files`: the only entries present in the artifact but not tracked by git were the auto-generated `MANIFEST.json`/`FILES.json` — nothing else leaked.
- Artifact went from carrying `.env.yml`, `molecule-logs/`, `.cache/`, and `collections/` to a clean 4.0K/15-file tarball of just the role and packaging metadata.
- Deleted the test tarball after the check.

Nothing was committed — the untracking is staged but not committed, per your instruction not to take that step unasked.
