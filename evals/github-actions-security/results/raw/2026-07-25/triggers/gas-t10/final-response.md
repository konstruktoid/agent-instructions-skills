## OIDC (OpenID Connect)

OIDC is an identity layer on top of OAuth 2.0 that lets one system prove its identity to another using short-lived, cryptographically signed tokens instead of a shared secret. In the GitHub Actions context, GitHub acts as an OIDC identity provider: during a workflow run, GitHub can mint a JSON Web Token (JWT) that asserts facts about that specific run — repository, branch/tag, workflow, environment, actor, etc. Cloud providers (AWS, Azure, GCP) can be configured to trust GitHub's OIDC provider and exchange that token for a short-lived cloud credential (e.g., an AWS STS session), scoped to whatever role/permissions you've defined.

## Why it's preferred over long-lived credentials

- **No stored secrets** — with OIDC there's no `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY` or service-account JSON key sitting in GitHub Secrets. Nothing to leak via a misconfigured log, a compromised dependency, or a malicious PR that dumps env vars.
- **Short-lived, single-use tokens** — the credential exchanged is typically valid for ~15–60 minutes and scoped to that one run. A long-lived key, once exfiltrated, is valid until manually rotated (often months or forever in practice).
- **Fine-grained trust conditions** — you configure the cloud-side trust policy to accept tokens only from specific repos, branches, environments, or even specific workflow files. Static credentials have no such binding — anyone with the secret can use it from anywhere.
- **No manual rotation burden** — long-lived keys require a rotation process that's frequently neglected; OIDC removes rotation entirely since tokens are minted fresh per run.
- **Better auditability** — cloud-side logs (CloudTrail, etc.) show the OIDC claims (repo, run ID, actor) tied to each assumed-role session, giving much richer forensic context than "key X was used."
- **Reduced blast radius** — compromise of the CI system or a secret leak doesn't hand an attacker a durable, reusable credential; the stolen token expires quickly and can't be replayed outside its intended conditions.

This is exactly why AWS's `aws-actions/configure-aws-credentials`, Azure's `azure/login`, and GCP's `google-github-actions/auth` all support (and recommend) OIDC-based `id-token: write` permission flows over static secret-based auth in GitHub Actions workflows.
