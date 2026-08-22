Everything confirmed and verified. Summary:

**What the 1.4.0 artifact holds:** the published tarball shipped a downloaded copy of `community.general` under `collections/` (the actual size bloat), plus three files carrying real machine data:
- `molecule-logs/converge-2026-08-18.log` — internal hostname `buildnode-04.corp.example.net`, IP `192.0.2.41`, username `mbraun`, and the home path `/home/mbraun/work/platform-storage`
- `.cache/ansible-compat/collection-paths.json` — the same home path
- `.env.yml` — a vault password, an API token, and an SSH username for staging

**Root cause:** two independent failures stacked. First, these four paths were committed to git in the initial commit (`.gitignore` only excluded `*.tar.gz`). Second, even for git-tracked files the build doesn't care about `.gitignore` — it walks disk and only respects `build_ignore` in `galaxy.yml`, and every entry there (`.ansible/`, `.cache/`, `.github/`, `collections/`) had a trailing slash, which `fnmatch` (what `build_ignore` uses) never matches against a path — so none of them ever excluded anything.

**Fix applied:**
- Untracked `.cache/`, `.env.yml`, `collections/`, `molecule-logs/` from git (`git rm --cached`) — they remain on disk untouched, as you asked, since you need them locally.
- Added them to `.gitignore` so they don't get re-committed.
- Rewrote `build_ignore` in `galaxy.yml` without trailing slashes, and extended it to also cover tracked developer-only files (`.github`, `ansible.cfg`, `.ansible-lint`) that ship no value to a consumer.
- Verified by actually building the collection and diffing the tarball's file list against `git ls-files`: artifact went from 31M to 3.4K, containing only the role's real files plus the build-generated `MANIFEST.json`/`FILES.json`. `ansible-lint` still passes clean (production profile, 0 findings).

One thing I did **not** do: the leaked hostname/credentials are still sitting in the repo's git history (the single `fixture baseline` commit). Untracking stops them from being in future commits and future builds, but anyone with that history — including anyone who already cloned the repo at 1.4.0 — can still recover them via `git show`. If that matters, rewriting history (e.g., `git filter-repo`) and rotating the leaked staging credentials would be the next step — let me know if you want that done, since it's a destructive/force-push operation I'd want your explicit go-ahead on.
