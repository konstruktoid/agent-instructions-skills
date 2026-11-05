Several things have to happen before the repo goes public. Making it public publishes every commit in history, not only the current tree, so most of the list is about disclosure.

I could only read the working tree. I had no shell access, so I couldn't query the GitHub API or scan git history. Nothing below about repository settings or history has been checked.

## What I found in the tree

- **`.github/workflows/deploy.yml` needs fixing before publication.**
  - It has `permissions: write-all` on a `pull_request` trigger.
  - It interpolates `${{ github.event.pull_request.title }}` directly into a `run:` step, which is a script-injection hole. Once the repo is public, anyone can open a PR with a crafted title.
  - Set `permissions: contents: read`, pass the title through an `env:` variable, and pin `actions/checkout` to a commit SHA.
- **There is no `SECURITY.md`, `CODEOWNERS`, `CONTRIBUTING.md` or `LICENSE`.**
- **A pattern search of the current files for keys, tokens and passwords found nothing.** That does not cover history.

## Before the switch (next week)

1. **Scan the full history for credentials.** Use gitleaks or trufflehog across all branches and tags, and check old commits, deleted files and PR refs.
   - Rotate anything found first. Rewriting history doesn't make an exposed secret safe.
   - Also look for internal hostnames, emails and customer data, not only secrets.
2. **Check the Actions configuration.** Set the default workflow token to read-only and restrict allowed actions to an allowlist.
   - Public repos can run workflows from fork PRs, so require approval for outside contributors.
   - Review repo and environment secrets, and remove any the workflows don't need.
3. **Add a `LICENSE`.** Without one, the code is public but not reusable, and that is probably not what you want.
4. **Add `SECURITY.md` with a private contact and a response time, and enable private vulnerability reporting.**
5. **Protect the default branch.** A ruleset in active mode should block force pushes and deletion, require a PR, require named status checks with `integration_id`, and require review plus conversation resolution. Add `CODEOWNERS` covering `.github/workflows/`, dependency manifests and release config.
6. **Review access.** Check collaborators, deploy keys and teams for least privilege. Remove stale ones.
7. **Turn on scanning.** Enable secret scanning, push protection, dependency alerts and code scanning on PRs. Committing a lockfile and adding Dependabot with a cooldown is also part of the baseline.
8. **Review the content for anything not meant to be public.** That includes `README.md`, docs, issues and PRs you plan to keep, and any evals or results directories. The `results/` directory in the git status is untracked. Make sure it stays out of the repo, or review it before committing.
9. **Check forks and Pages.** Private forks are detached or deleted when visibility changes, and Pages or packages may have their own visibility.

## The switch itself

Changing visibility is irreversible in practice, because the content may be cloned, cached or indexed immediately. I won't do it without your explicit go-ahead. I'll also confirm the checklist above first and read each setting back afterwards.

If you'd like, I can fix `deploy.yml` and draft `SECURITY.md`, `CODEOWNERS` and a ruleset JSON now. If you grant shell access, I can also run the history scan and read the live repo settings.
