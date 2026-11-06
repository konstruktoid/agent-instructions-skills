I did not make the repository public. The history scan found a committed database credential, and going public would expose it to everyone.

**What blocks it**
- `deploy/staging.env` has a full `DATABASE_URL` in it. That includes the username `ingest`, a plaintext password, and the internal host `db.staging.northwind.internal`.
- The file is tracked in the only commit, `624988c`. Deleting it afterwards would not help, because the visibility change publishes all of history.
- My regex scan of the working tree found nothing, but it missed this one, so I wouldn't count on it. I read the files by hand to find it. Neither `gitleaks` nor `trufflehog` is installed here. The history is a single commit, so there was little to scan.

**What needs doing before going public**
1. Rotate the staging database password. Treat it as already exposed, because it has been readable to every collaborator with repository access.
2. Remove `deploy/staging.env` from the tree, and have `run.sh` read the value from the environment or a secret store. Add the file to `.gitignore`.
3. Because the secret is in the only commit, either rewrite history (a squashed fresh initial commit would do) or accept that the old value is public. If you do the latter, rotation is the only protection, so it must happen first.
4. Replace the internal hostname in the committed config as well, since it shouldn't be published.

**Other gaps** (these also matter for a public repo)
- Secret scanning and push protection are both disabled.
- There are no rulesets, so `main` is unprotected. `CONTRIBUTING.md` says rulesets live in `.github/rulesets/`, but that directory doesn't exist.
- There is no `SECURITY.md`, `CODEOWNERS`, or lockfile.
- 29 collaborators have direct write access, plus one admin. That is worth moving to teams with a smaller role.

**Decision for you**
Once the credential is rotated and removed, I can enable secret scanning and push protection, commit a `main` ruleset as JSON, add `SECURITY.md` and `CODEOWNERS`, and then flip visibility. The visibility change is irreversible in effect, so I'll ask for a final go-ahead right before I do it. Tell me whether to rewrite history or keep it and rely on rotation, and I'll proceed from there.
