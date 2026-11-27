# OIDC and why it beats long-lived cloud credentials

## What OIDC is

**OpenID Connect (OIDC)** is an identity layer built on OAuth 2.0. An **identity provider (IdP)** issues a signed **ID token**, which is a JWT. The token contains claims about who or what is authenticating, and a **relying party** checks the token before trusting it.

In CI/CD and workload identity, it works like this:

1. **The CI platform acts as the IdP.** GitHub Actions, GitLab, CircleCI and similar systems can mint a short-lived JWT for each job. The JWT carries claims such as:
   - `iss`: the issuer, e.g. `https://token.actions.githubusercontent.com`
   - `sub`: the subject, e.g. `repo:org/repo:ref:refs/heads/main` or `repo:org/repo:environment:prod`
   - `aud`: the intended audience, e.g. `sts.amazonaws.com`
   - context such as `repository`, `ref`, `workflow`, `job_workflow_ref` and `environment`
2. **The cloud provider is set up to trust that issuer.** Examples are an AWS IAM OIDC provider, GCP Workload Identity Federation and an Azure federated credential. A trust policy says which claims are allowed to assume which role.
3. **The job exchanges its token.** It sends the JWT to the cloud's security token service (e.g. AWS `AssumeRoleWithWebIdentity`). The cloud checks the signature against the issuer's public keys (JWKS), then checks the claims against the trust policy.
4. **The cloud returns short-lived credentials.** These usually last 15 minutes to 1 hour and are scoped to that one role.

No secret is stored anywhere. The job proves *what it is*, not *what it knows*.

## Why it's preferred over long-lived credentials

| Concern | Long-lived keys (e.g. `AWS_ACCESS_KEY_ID` in repo secrets) | OIDC federation |
|---|---|---|
| **Secret storage** | A static secret sits in CI settings, and often gets copied into other places. | Nothing to store. Credentials are minted when the job needs them. |
| **Blast radius if leaked** | Valid until someone notices and rotates it, which can take months or years. | Expires within minutes to an hour. |
| **Rotation** | Manual, error-prone and often skipped. | Not needed, because every run gets new credentials. |
| **Scoping** | Anyone holding the key can use it from anywhere. | The trust policy can restrict access by repo, branch, tag, environment or the workflow that calls it. |
| **Exfiltration risk** | Secrets can leak through logs, `pull_request_target` mistakes, compromised actions or debug output. | A stolen token is short-lived and audience-bound. It's only worth something during the job. |
| **Auditability** | Cloud logs show "the CI user" did something. | Cloud logs carry the session's identity claims (e.g. repo and ref), so you can trace actions back to a specific run. |
| **Offboarding / sprawl** | Keys outlive the projects and people that created them. | Trust is tied to config. Delete the role or trust policy and access is gone. |

## Caveats: OIDC is only as strong as its trust policy

- **Always constrain `sub` (and `aud`).** If the trust policy only checks the issuer, *any* GitHub repository in the world can assume your role. Pin it to a specific repo plus a branch or environment, e.g. `repo:my-org/my-repo:environment:production`, and avoid broad wildcards.
- **Prefer environment-based subjects for deployments.** That way GitHub environment protection rules (required reviewers, branch restrictions) also gate access to the cloud.
- **Grant the token permission only where it's needed.** In GitHub Actions, add `permissions: id-token: write` only to the jobs that actually exchange the token, not to the whole workflow.
- **Keep the cloud role least-privilege.** A short-lived admin credential is still an admin credential.
- **Watch untrusted triggers.** If a workflow triggered by a fork PR (e.g. through `pull_request_target`) can request an ID token and match your trust policy, attacker-controlled code can get cloud access.

**In short:** OIDC replaces "a secret we hope never leaks" with "a short-lived credential tied to this specific job." That removes rotation work and greatly limits the damage from a compromise.
