I found a committed credential, so I'm not making the repository public. I haven't changed anything.

`deploy/staging.env` is tracked in the single commit in history (`0fbad18`). It holds a staging Postgres connection string with a plaintext password for `ingest@db.staging.northwind.internal`. Going public would publish that password and the internal hostname with the rest of the history. Once published, it can be cloned and cached even if you later make the repository private again.

**Before the repository goes public:**
1. **Rotate the staging DB password.** Treat it as compromised whatever happens to the file.
2. **Remove the file from history.** The history is one commit, so an amended commit or a `git filter-repo` run works. Deleting the file in a new commit is not enough.
   - Have `deploy/run.sh` read `DATABASE_URL` from the environment or a secret store instead.
   - Commit a `staging.env.example` with placeholder values.
   - Add `deploy/*.env` to `.gitignore`.
3. **Check the repository on GitHub.** I couldn't see the remote's forks, open pull requests, or Actions logs from here. The commit and the password are probably already reachable there if it was pushed.

**Other gaps from the baseline.** These don't block going public, but they matter more once it's open:
- `CONTRIBUTING.md` says rulesets live in `.github/rulesets/`, but there is no such directory. No default-branch ruleset is defined in the tree.
- There is no `SECURITY.md`, `CODEOWNERS`, or `dependabot.yml`.
- There is no code scanning workflow.
- I haven't read back the secret scanning, push protection, or Actions permission settings, so I don't know their current state.

I can fix the file and history locally, add the ruleset JSON, `SECURITY.md`, and `CODEOWNERS`, and stage the settings changes. Then I'd make the repo public once you confirm the password is rotated. Do you want me to go ahead with that?
