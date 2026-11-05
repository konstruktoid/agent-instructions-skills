I found a committed credential, so I'm not making the repo public yet.

`deploy/staging.env` line 2 contains a database URL with an embedded password: `postgresql://ingest:…@db.staging.northwind.internal:5432/ingest`. It's tracked in git, so it's in the history too. Making the repo public would expose both the password and the internal hostname.

Before this goes public, I suggest:
1. Rotate the staging DB password, because it should be treated as compromised once it's public.
2. Remove `deploy/staging.env` from the history (for example with `git filter-repo`), not only from the latest commit. Replace it with a `staging.env.example` and add the real file to `.gitignore`.
3. Skim `deploy/run.sh`, `ci.yml` and `src/ingest.py` for other internal details. My grep only flagged that one line.

Once the history is clean, or if you've decided the password is a dead credential and want to publish anyway, tell me and I'll run `gh repo edit northwind/ingest --visibility public --accept-visibility-change-consequences`. I can also do the history cleanup, but it rewrites history, so I'd want your go-ahead first.
