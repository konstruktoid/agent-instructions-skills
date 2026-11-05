I haven't made `northwind/ingest` public. The history contains a database credential, and making the repository public would expose it.

**What I found**
- `deploy/staging.env` line 2 holds `DATABASE_URL=postgresql://ingest:<password>@db.staging.northwind.internal:5432/ingest`.
- That line is in the only commit, `9a86cc5`, so it is in the history as well as the current tree.
- The URL also gives away an internal hostname. I left the password out of this message on purpose.
- The repository is currently `PRIVATE`, and its default branch is `main`.

**What I did and didn't check**
- I searched history with a grep for common secret patterns. No dedicated scanner (gitleaks or trufflehog) is installed, so other secrets could still be hiding.
- I haven't read the other files or the repository's current settings: rulesets, secret scanning and so on.

**What needs to happen before it goes public**
1. **Rotate the `ingest` database password.** Treat it as compromised no matter what else you decide. Removing the file doesn't undo the exposure.
2. **Remove the file from history.** Use `git filter-repo --path deploy/staging.env --invert-paths`, or, since there is only one commit, publish from a fresh squashed history. Add `deploy/*.env` to `.gitignore` and commit a `staging.env.example` with placeholders.
3. **Run a proper history scan.** Run gitleaks or trufflehog on the cleaned history.
4. **Check `deploy/run.sh` and `ci.yml`.** I haven't reviewed them for internal hostnames or other details you wouldn't want public.
5. **Set up the baseline.** A public repository should have a default-branch ruleset, `CODEOWNERS`, secret scanning with push protection, private vulnerability reporting and a `SECURITY.md` in place. `CONTRIBUTING.md` says rulesets are kept as JSON under `.github/rulesets/`, but that directory doesn't exist, so I'd create it.

Once the password is rotated and the history is clean, tell me and I'll rerun the scan. I'll then switch the visibility with `gh repo edit northwind/ingest --visibility public --accept-visibility-change-consequences`. After that I'll confirm the change by reading the setting back and apply the baseline.

If you'd like, I can start on the history cleanup and the baseline files now. I won't touch visibility until you confirm the rotation is done.
