## OIDC (OpenID Connect)

OIDC is an identity layer on top of OAuth 2.0 that lets one system prove its identity to another using short-lived, cryptographically signed tokens instead of a shared secret. In CI/CD (e.g., GitHub Actions), the CI provider acts as an identity provider: for each workflow run it can mint a JWT that asserts facts like "this is repo X, workflow Y, branch/tag Z, triggered by event E." Your cloud provider (AWS, Azure, GCP, etc.) is configured to trust that identity provider and, when it sees a valid token matching a pre-defined trust policy, hands out temporary credentials scoped to a specific role — no secret ever changes hands.

## Why it's preferred over long-lived credentials

- **No secrets to steal or leak.** Long-lived access keys stored as CI secrets can be exfiltrated via logs, malicious PRs, compromised dependencies, or misconfigured workflows — and once leaked they're valid until manually rotated. OIDC tokens are minted per-run and expire in minutes.
- **No rotation burden.** Static keys require manual/periodic rotation; forgetting to rotate is a common source of breaches. OIDC eliminates the credential lifecycle entirely — trust is established via configuration, not a stored value.
- **Fine-grained, auditable trust.** The trust policy can restrict exactly which repo, branch, tag, or environment is allowed to assume a role (e.g., only `main` branch pushes on `myorg/myrepo`), which is much more precise than a single shared key usable from anywhere.
- **Reduced blast radius.** If a workflow is compromised, an attacker gets a short-lived, narrowly-scoped credential tied to that specific run's claims — not a standing key they can reuse indefinitely from anywhere.
- **Centralized revocation.** Compromising the identity federation trust is harder than compromising one stored secret, and you can revoke trust at the IdP/cloud config level without touching every repo's secrets.

The tradeoff is more upfront setup (configuring the OIDC trust relationship and IAM role policy), but it removes an entire class of credential-leak risk, which is why it's the recommended approach for CI-to-cloud authentication (e.g., `aws-actions/configure-aws-credentials`, Azure's `azure/login`, GCP's `google-github-actions/auth` all support OIDC-based auth).
