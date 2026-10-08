# OIDC and why it beats long-lived cloud credentials

## What it is

OpenID Connect (OIDC) is an identity layer built on OAuth 2.0. In CI/CD, such as GitHub Actions, it lets a workflow prove who it is to a cloud provider without holding a stored secret.

1. When a job runs, the CI platform's identity provider issues a short-lived, signed JSON Web Token (JWT) for that specific run.
2. The token carries claims describing the run: the repository, branch or tag, environment, workflow, and the triggering event. Examples are `sub`, `aud`, `iss`, `repository`, and `ref`.
3. The job sends the token to the cloud provider (AWS, Azure, GCP, Vault, and so on).
4. The cloud provider checks the signature against the CI platform's public keys. It also checks that the claims match a trust policy you configured, such as "only `org/repo` on `main` may assume this role".
5. If everything matches, the cloud provider returns temporary credentials that typically expire within minutes to an hour.

## Why it's preferred over long-lived credentials

| Concern | Long-lived keys (stored as secrets) | OIDC |
|---|---|---|
| **Secret storage** | The key lives in the CI secret store, and often gets copied elsewhere too. | Nothing sensitive is stored. |
| **Leak impact** | A leaked key works from anywhere until someone notices and revokes it. | The token is short-lived and bound to the audience and claims. A stolen one is mostly useless after it expires. |
| **Rotation** | Manual, often skipped, and it breaks pipelines when done. | Automatic, because every run gets fresh credentials. |
| **Scoping** | Keys are usually broad and shared across repos and environments. | Trust policies can restrict by repo, branch, environment, or workflow. |
| **Auditability** | Logs show "the CI user" and you can't tell which run acted. | Each session maps to a specific run and identity, so logs can be traced to it. |
| **Blast radius from PRs and forks** | A compromised step or dependency can exfiltrate the key. | Fork PRs and untrusted triggers can be denied by claim conditions. Exfiltrated credentials expire quickly. |
| **Offboarding** | You must remember to revoke keys when people or repos change. | Nothing to revoke, because trust is tied to repo and workflow identity. |

In short, OIDC replaces "a secret that proves you have the key" with "a short-lived assertion of who you are and where you're running". That removes a whole class of credential theft and rotation problems.

## Caveats

- **Trust policies must be tight.** A policy like `repo:org/*` or one with no `sub` condition lets any repo in the org, or sometimes any repo at all, assume the role. Pin the `sub` claim to the repo and to a branch or environment.
- **Grant the CI job permission to request the token.** In GitHub Actions that is `permissions: id-token: write`. Scope it to the jobs that need it rather than the whole workflow.
- **The cloud role still needs least privilege.** OIDC fixes how you authenticate, not what the role is allowed to do.
- **Not every service supports it.** Third-party SaaS APIs that only issue static API keys still need stored secrets, so keep those narrowly scoped and rotated.

If you'd like, I can review the OIDC setup in one of your workflows or draft a trust policy for a specific cloud.
