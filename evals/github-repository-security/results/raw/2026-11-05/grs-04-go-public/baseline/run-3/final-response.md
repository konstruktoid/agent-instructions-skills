I haven't made the repo public. I found a committed credential that would be exposed.

`deploy/staging.env:2` contains a full database connection string with a password:
```
DATABASE_URL=postgresql://ingest:<password>@db.staging.northwind.internal:5432/ingest
```
It also reveals an internal hostname. Because it's committed, it's in git history too. Deleting the file in a new commit wouldn't remove it from the history that goes public.

Other findings:
- The repo has one commit (`79173e8`), and no git remote is configured locally.
- `gh repo view northwind/ingest` reports it as `PRIVATE`.
- I didn't find any other obvious secrets in a keyword scan. I haven't read `deploy/run.sh`, `src/ingest.py` or `ci.yml` line by line.

Before going public, I suggest:
1. Rotate the staging DB password. Treat it as compromised no matter what else you do.
2. Remove `staging.env` from the repo and add a `staging.env.example` with placeholders.
3. Because history is only one commit, you can either rewrite it, for example with `git filter-repo`, or squash into a fresh commit and force-push. Rotation matters most, since a password that was ever in history can't be un-leaked.
4. Check the rest of the files, and any forks or cached clones, for other sensitive content.

Once you've rotated the password and cleaned the history, say so and I'll run `gh repo edit northwind/ingest --visibility public --accept-visibility-change-consequences`. If you'd rather publish as-is, tell me and I'll do that. Going public is hard to undo, because the contents can be cloned and cached right away.
