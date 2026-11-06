The repo is missing most of what a public repo needs. In the working tree I found only `.github/workflows/deploy.yml`. There's no `LICENSE`, `SECURITY.md`, `CODEOWNERS`, `CONTRIBUTING.md` or secret-scanner config. I haven't read any live GitHub settings yet.

## Before the switch

**1. Scan the full history for secrets (the blocker).**
- Going public publishes every commit, branch and tag, not only the current tree. Deleted files and old commits count.
- Run a history scanner such as gitleaks or trufflehog across all refs.
- Rotate anything it finds. Rewriting history doesn't make a leaked credential safe, and forks and caches can keep copies.
- Also check for internal hostnames, internal addresses, personal emails and customer data in commits, issues and PR text.

**2. Review `.github/workflows/deploy.yml`.**
- Check for embedded secrets and for any dependence on self-hosted runners. Public repos shouldn't use self-hosted runners, because fork PRs can run code on them.
- Check for `pull_request_target` or other triggers that fork PRs could abuse.
- Pin actions, set the token to read-only, and move the deploy to OIDC instead of long-lived secrets.
- Review the repository and environment secrets. Make sure the deploy is gated by a protected environment with reviewers.

**3. Add the missing files.**
- `LICENSE`. Without one, the code is public but nobody has a right to use it.
- `SECURITY.md` with a private contact and a response time, plus private vulnerability reporting turned on.
- `CODEOWNERS` covering workflows, dependency manifests, release config and any agent-facing content.
- `CONTRIBUTING.md`, and a README that makes sense to outsiders.

**4. Enable protections.** Do this before the switch, since some features only become available or change behavior once the repo is public.
- Secret scanning and push protection.
- Dependency alerts, plus a committed lockfile and scheduled updates.
- Code scanning on PRs.
- An active ruleset on the default branch: PR required, approvals, stale review dismissal, named status checks tied to `integration_id`, no force pushes or deletion.
- Actions restricted to an allowlist, and fork-PR workflows requiring approval.

**5. Review access.**
- Trim collaborators to the smallest role they need.
- Make deploy keys read-only unless a write need is stated.
- Confirm who can bypass the rules.

**6. Get sign-off.** Legal, security or comms approval if you need it. Decide in advance who owns incoming issues and PRs.

## Making the switch

- Changing visibility is outward-facing and effectively irreversible. Once the code has been public, assume it was copied. I won't change it without your explicit go-ahead on the day.
- Repeat the secret scan against the final HEAD just before switching.

## What I can do now

Give me the `owner/repo` and I'll do the following:
- Read the live settings, rulesets, collaborators, keys and secrets.
- Run the history scan.
- Draft the missing files and a ruleset JSON for you to review.

I won't apply anything outward-facing without your approval.
