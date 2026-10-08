# OIDC and why it beats long-lived cloud credentials

## What OIDC is

OpenID Connect (OIDC) is an identity layer built on OAuth 2.0. In CI/CD, such as GitHub Actions, it lets a workflow prove who it is to a cloud provider (AWS, Azure, GCP, HashiCorp Vault and others) without a stored secret.

1. **The workflow requests a token.** With `permissions: id-token: write`, the job asks the CI platform's OIDC provider for a signed JSON Web Token (JWT).
2. **The token carries claims about the run.** These include the issuer, the audience, and a `sub` (subject) such as `repo:org/repo:ref:refs/heads/main` or `repo:org/repo:environment:prod`. Others identify the repository, workflow, branch, and so on.
3. **The cloud provider verifies the token.** It checks the signature against the issuer's public keys, which it fetches from the issuer's published metadata. It also checks that the claims match a trust policy you configured, for example "only `org/repo` on `main` may assume this role".
4. **The provider issues short-lived credentials.** The workflow exchanges the JWT for temporary cloud credentials, usually valid for about an hour or less, scoped to a specific role.

The trust relationship is configured once in the cloud account. Nothing secret is stored in the CI system.

## Why it is preferred over long-lived credentials

| Concern | Long-lived keys (e.g. `AWS_ACCESS_KEY_ID` secrets) | OIDC |
|---|---|---|
| **Leak impact** | A leaked key works until someone notices and rotates it. | Tokens expire in minutes, so a leaked one is nearly useless afterward. |
| **Secret storage** | The key sits in the repo or org secrets, where it can be exfiltrated by compromised actions, script injection, or malicious PRs. | There is no stored cloud secret to steal. |
| **Rotation** | Manual, easy to neglect, and often breaks pipelines. | Automatic, because every run gets fresh credentials. |
| **Scoping** | Keys tend to be broad and shared across repos. | Trust policies can bind to a specific repo, branch, environment, or workflow, so a fork or feature branch can't assume a prod role. |
| **Auditability** | CloudTrail shows "the CI user" did it. | Sessions are tied to a specific run and identity, which makes attribution easier. |
| **Operations** | Someone has to create, distribute, and revoke the keys. | Access is managed as IAM and trust policy, which can be reviewed as code. |

## Caveats

- **Trust policies must be tight.** A policy that only checks the issuer, or uses a wildcard `sub`, lets any repo on the platform assume your role. Always pin the `sub` and `aud` claims.
- **`id-token: write` should be granted per job.** Grant it only to the jobs that need it, not workflow-wide.
- **Untrusted code can still use the token.** If an attacker can run code in the job, they can request a token during that run. OIDC limits the blast radius and lifetime, but it doesn't replace injection hardening or least-privilege roles.

In short, OIDC replaces "a secret that proves you're allowed" with "a short-lived, verifiable statement of who you are". That removes the most commonly stolen asset in CI pipelines.
