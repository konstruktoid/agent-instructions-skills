# OIDC and why it beats long-lived cloud credentials

## What OIDC is

**OpenID Connect (OIDC)** is an identity layer built on OAuth 2.0. An *identity provider* issues a signed JSON Web Token (JWT) that says who or what the bearer is. A *relying party* checks the signature against the provider's published public keys (its JWKS endpoint) and then trusts what the token says.

In CI/CD, the CI platform is the identity provider. GitHub Actions, for example, can mint a token for each job from `https://token.actions.githubusercontent.com`. The token's claims describe the job that is running:

- `repository`: `my-org/my-repo`
- `ref`: `refs/heads/main`
- `environment`: `production`
- `workflow_ref`, `job_workflow_ref`, `event_name`, `repository_owner_id`, and others
- `sub`: a composite subject such as `repo:my-org/my-repo:environment:production`
- `aud`: the intended audience, such as `sts.amazonaws.com`
- a short expiry, usually minutes

The cloud provider (AWS, Azure, GCP, Vault and so on) is set up to **trust that issuer** and to **exchange the token for short-lived cloud credentials**, but only when the claims match a policy you define.

## How the flow works (GitHub → AWS example)

1. The workflow has `permissions: id-token: write`. Without this, the job can't request a token.
2. The job asks GitHub's OIDC provider for a JWT with the right audience.
3. The job sends the JWT to AWS STS through `AssumeRoleWithWebIdentity`.
4. AWS checks the signature and the issuer. It then checks the role's trust policy, for example that `sub` equals `repo:my-org/my-repo:environment:production`.
5. AWS returns temporary credentials that last about an hour by default, or less if you configure it.
6. The credentials expire on their own. Nothing is stored anywhere.

```yaml
permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    environment: production
    runs-on: ubuntu-latest
    steps:
      - uses: aws-actions/configure-aws-credentials@<sha>  # pinned
        with:
          role-to-assume: arn:aws:iam::123456789012:role/deploy-prod
          aws-region: eu-north-1
```

## Why it's preferred over long-lived credentials

| Concern | Long-lived keys (e.g. `AWS_ACCESS_KEY_ID` in secrets) | OIDC federation |
|---|---|---|
| **Lifetime** | Valid until someone rotates or revokes them, often months or years | Minutes to an hour, then they expire automatically |
| **Blast radius if leaked** | Usable from anywhere, by anyone, until revoked | A leaked token or credential soon expires. The JWT only works for the audience and the trust policy it was issued for |
| **Storage** | Kept as a secret in the CI platform, copied between repos, sometimes in `.env` files | No cloud secret is stored. The trust relationship is just configuration |
| **Rotation** | Manual, easy to forget, and can cause outages | Not needed. Every run gets fresh credentials |
| **Scoping** | One key usually serves every branch, PR and workflow that can read the secret | Trust policies can limit access to a specific repo, branch, environment, tag or reusable workflow |
| **Auditability** | Cloud logs show "key AKIA… did X" | Cloud logs show the assumed role and session, which traces back to a specific repo and run |
| **Off-boarding / sprawl** | Keys outlive projects and people and are hard to inventory | Delete the role or the trust policy and access ends |

In short: you stop holding a **secret** and hold a **verifiable identity** instead. The cloud trusts a cryptographic statement about which workflow is running, not whoever happens to have a copied password.

## Caveats: OIDC is only as strong as its trust policy

- **Scope the `sub` claim tightly.** A trust policy that only checks `repo:my-org/*`, or only checks `aud`, lets any repo in the org assume the role, or in the worst misconfigurations any GitHub repo at all. Pin to a specific repo plus an `environment` or `ref`.
- **Prefer `environment`-based subjects for production.** GitHub Environments can require reviewers and allow only certain branches, which gates who can get a token for prod.
- **Watch untrusted triggers.** A `pull_request_target` or `workflow_run` job with `id-token: write` that runs attacker-controlled code can mint a valid token. Grant `id-token: write` only to jobs that need it, never at the top level of the workflow.
- **Consider immutable claims.** Use `repository_id` and `repository_owner_id`, or GitHub's customizable `sub` templates, so a renamed or recreated repo with the same name can't inherit trust.
- **Least privilege still applies** to the role itself. Short-lived admin credentials are still admin credentials.

If you'd like, I can review a specific workflow or cloud trust policy against these points.
