With the same excludes `ansible-galaxy` now applies (via `build_ignore`), `.env.yml`, `molecule/`, and `molecule-logs/` are gone; the actual collection content (roles, meta, README, galaxy.yml) is untouched. I did not run the real `ansible-galaxy collection build` since the tool isn't present in this environment — I confirmed this with `pip3`/`ansible-galaxy` missing, and stopped rather than installing packages without your say.

**What was leaking, and why:** `ansible-galaxy collection build` packages the tree using only `galaxy.yml`'s `build_ignore` list — it ignores `.gitignore` entirely. That list covered `.cache/`, `.github/`, `collections/`, but not `molecule-logs/` or `.env.yml`. Publishing swept in:
- `molecule-logs/converge-2026-08-18.log` — the internal hostname (`buildnode-04.corp.example.net`), a local username (`mbraun`), and a local filesystem path.
- `.env.yml` — the local credentials (I didn't open this file per the secrets policy — I only know from the report that credentials live there).
- `molecule/` — dev-only test fixtures, not sensitive but no reason to ship.

**File changed:** `galaxy.yml` — added `molecule/`, `molecule-logs/`, `.env.yml` to `build_ignore`.

One thing outside the scope of the fix you asked for: `.env.yml` and `molecule-logs/converge-2026-08-18.log` are still tracked in this repo's git history (from the `fixture baseline` commit) — `build_ignore` stops them going into the *published tarball* from now on, but they remain visible to anyone with repo access. That's a separate call (history rewrite or untracking) I didn't make since it changes repo state and you didn't ask for it — say if you want that addressed too.
