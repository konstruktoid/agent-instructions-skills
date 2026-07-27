**OIDC (OpenID Connect)** is an identity layer on top of OAuth 2.0. In CI/CD (e.g., GitHub Actions), it lets your workflow request a short-lived, cryptographically signed token from the CI provider and exchange it with a cloud provider (AWS, Azure, GCP) for temporary credentials — no secret needs to be stored anywhere.

**Why it's preferred over long-lived credentials (e.g., static AWS access keys stored as secrets):**

- **No standing secrets to leak** — there's no access key sitting in repo secrets that can be exfiltrated via a compromised dependency, malicious PR, or log leak.
- **Short-lived tokens** — OIDC-issued credentials expire in minutes/hours, shrinking the window of usefulness if one is ever exposed.
- **Fine-grained trust policy** — the cloud provider's IAM trust relationship can scope exactly which repo, branch, workflow, or environment is allowed to assume a role, rather than "anyone with this secret."
- **No manual rotation** — nothing to rotate or accidentally forget to rotate; the trust is federated, not credential-based.
- **Better auditability** — cloud-side logs show which specific workflow/run assumed the role via the token claims, rather than an opaque static key.

In short: static keys are a durable secret that grants access forever until someone remembers to revoke it; OIDC replaces that with a short-lived, provably-scoped token minted per run — much smaller blast radius if a workflow or repo is compromised.
