I haven't changed anything. I could only read the working tree, because this session has no shell and no GitHub API access. I couldn't check the live repository settings or scan git history. Those are the most important checks before going public.

## Must happen before the switch

**1. Scan the full git history for secrets.**
- Making the repository public publishes every commit, not just the current tree.
- A regex scan of the current tree for common token and key patterns found nothing.
- That scan doesn't cover history, so run a history scanner such as gitleaks or trufflehog over all branches and tags.
- Rotate anything found. Rewriting history doesn't help once forks and caches exist.
- Run it before the flip, not after.

**2. Fix `.github/workflows/deploy.yml`.** It is unsafe on a public repository.
- `permissions: write-all` gives the token full write access. Set the default to `contents: read` and grant more per job only where needed.
- `${{ github.event.pull_request.title }}` is interpolated directly into a `run:` step. That is script injection, and on a public repository anyone can open a PR and exploit it. Pass the value through an `env:` variable instead.
- `actions/checkout@v4` is pinned to a tag, not a commit SHA. Pin it to a SHA.
- The workflow triggers on `pull_request` and has write permissions. Once the repository is public, check what secrets and deploy rights it can reach from fork PRs.

**3. Remove internal details.** `scripts/backup.sh:11` contains `backup@archive.example.internal`. Decide whether you want to publish that hostname and the backup layout. Also check commit author emails in history, since those become public too.

**4. Add the missing files.** None of these exist in the repo:
- `SECURITY.md`, with a private reporting channel and a response time.
- `CODEOWNERS`, covering `.github/workflows/`, `scripts/` and dependency manifests.
- `LICENSE`. Without one, the code is public but nobody has the right to use it.
- `CONTRIBUTING.md` (optional).

**5. Check the live repository settings.** Run these yourself or give me a shell with `gh`:
- Enable secret scanning and push protection.
- Enable private vulnerability reporting and dependency alerts.
- Add a ruleset on `main`: no force pushes, no deletion, PR required, one approval, stale approvals dismissed, and named status checks bound to their apps.
- Set the default workflow token to read-only and restrict allowed actions.
- Audit collaborators and deploy keys. Remove anything that shouldn't be visible or that has more access than it needs.
- Review stored Actions secrets and environments.
- Under fork-PR settings, require approval for outside contributors.

**6. Review the rest of the content.**
- Check issues, PRs, wikis and comments for private information, because they become public too.
- Check for private-repo-only links or references to other private repositories.
- Check that dependencies are all public and that their licenses are compatible.

## Order of work
1. Run the history scan, and rotate anything it finds.
2. Fix the workflow and scrub internal details.
3. Add `SECURITY.md`, `CODEOWNERS` and `LICENSE`.
4. Apply the ruleset and scanning settings, then read each setting back through a separate API call.
5. Get explicit approval, then flip the visibility. I'd want your go-ahead for that step specifically, since it is hard to undo.

If you give me a shell with `gh` and permission to run a history scanner, I can run steps 1 and 5 and prepare the workflow fix and the missing files for review.
