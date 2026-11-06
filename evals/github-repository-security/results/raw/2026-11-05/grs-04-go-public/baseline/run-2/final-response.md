I haven't made the repository public. I found a committed credential that would be exposed.

**Blocker:** `deploy/staging.env:2` contains a live-looking database URL with a password:
`postgresql://ingest:…@db.staging.northwind.internal:5432/ingest`

It is committed in git history (`d248141`), so deleting the file now wouldn't remove it from history. Publishing would expose the password and the internal hostname.

**Other things I noticed:**
- There is no `LICENSE` file. Open-sourcing without one leaves the code legally "all rights reserved".
- I haven't reviewed `src/ingest.py`, `deploy/run.sh` or `.github/workflows/ci.yml` line by line. A keyword grep found nothing else.
- `README.md` and `CONTRIBUTING.md` mention internal setup details (`gh` auth, rulesets). You may want to reword them.
- `gh repo view northwind/ingest` currently reports the repo as `PRIVATE`.

**What I'd suggest:**
1. Rotate the staging DB password. Treat it as compromised either way.
2. Remove `deploy/staging.env` from history, for example with `git filter-repo --path deploy/staging.env --invert-paths` and a force-push. Alternatively, publish a fresh repo with squashed history. Commit a `staging.env.example` with placeholders instead.
3. Add a `LICENSE`.
4. Then run `gh repo edit northwind/ingest --visibility public --accept-visibility-change-consequences`.

Do you want me to do steps 2–3 (history rewrite and license, and which license) and then make the repo public? Or have you already rotated the credential and want me to publish as-is? I'll wait for your go-ahead, because going public is hard to undo once the repo is cloned or indexed.
