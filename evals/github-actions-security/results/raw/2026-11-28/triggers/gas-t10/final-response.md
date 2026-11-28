# OIDC and why it beats long-lived cloud credentials

## What OIDC is

**OpenID Connect (OIDC)** is an identity layer built on OAuth 2.0. An *identity provider* issues a signed, short-lived JSON Web Token (JWT) that says who the caller is. A *relying party* checks the signature against the issuer's public keys and decides whether to trust the claims in the token.

In CI/CD, and in GitHub Actions in particular, the flow works like this:

1. **The CI platform is the identity provider.** GitHub runs an OIDC issuer at `https://token.actions.githubusercontent.com`. When a job has `permissions: id-token: write`, it can ask that issuer for a JWT describing itself.
2. **The token carries claims about the job.** For example:
   - `sub`: `repo:my-org/my-repo:ref:refs/heads/main` or `repo:my-org/my-repo:environment:production`
   - `aud`: who the token is meant for, e.g. `sts.amazonaws.com`
   - others such as `repository`, `ref`, `environment`, `job_workflow_ref`, `actor`, `event_name`
3. **The cloud provider trusts that issuer.** You set up a trust relationship once: an AWS IAM OIDC provider and role, an Azure federated credential, or a GCP Workload Identity Pool. Its conditions say something like: "only accept tokens where `sub` equals `repo:my-org/my-repo:environment:production`."
4. **The token is exchanged for cloud credentials.** The job sends the JWT to the cloud's security token service (e.g. AWS `AssumeRoleWithWebIdentity`). That service validates the signature and claims, then returns temporary credentials that usually expire within an hour.

```yaml
permissions:
  id-token: write   # allow requesting the OIDC JWT
  contents: read

jobs:
  deploy:
    environment: production
    runs-on: ubuntu-latest
    steps:
      - uses: aws-actions/configure-aws-credentials@<pinned-sha>
        with:
          role-to-assume: arn:aws:iam::123456789012:role/gha-deploy-prod
          aws-region: eu-north-1
```

No cloud secret is stored anywhere in GitHub.

## Why it's preferred over long-lived credentials

| Concern | Long-lived keys (e.g. `AWS_ACCESS_KEY_ID` in secrets) | OIDC federation |
|---|---|---|
| **Secret at rest** | A static key sits in repo or org secrets and can leak, get copied or be exfiltrated | Nothing to store; the JWT is minted per job |
| **Lifetime** | Valid until someone rotates it, often months or years | Minutes to an hour, then useless |
| **Blast radius of a leak** | Anyone with the key gets full access from anywhere, indefinitely | A stolen token expires quickly and only works within its audience and trust conditions |
| **Scoping** | Any workflow, branch or fork-triggered job that can read the secret can use it | The trust policy can pin a specific repo, branch, tag, environment or reusable workflow |
| **Rotation** | Manual and error-prone, so often skipped | Not needed; every run gets fresh credentials |
| **Auditability** | Cloud logs show "the CI user" | Cloud logs show the role session, and the token claims link it to a specific repo, ref and run |
| **Offboarding / cleanup** | Old keys pile up and get forgotten | Deleting the trust relationship revokes access immediately |

The main gain is that **identity replaces a shared secret**. Instead of "whoever holds this string is trusted," the rule becomes "this exact workflow, on this branch or environment, in this repo, is trusted right now."

## Pitfalls that weaken OIDC

- **Overly broad `sub` conditions.** For example `repo:my-org/*` or a bare wildcard. With a wildcard, any repo, branch or PR workflow could assume a production role. Pin the exact repo plus the branch or environment.
- **Not checking `aud`.** Always restrict the audience as well.
- **Granting `id-token: write` workflow-wide.** Grant it only to the jobs that need it, and don't grant it to jobs that run untrusted PR code.
- **Over-privileged roles.** OIDC fixes how credentials are delivered, not what they can do. The assumed role still needs least privilege.
- **Using environments without protection rules.** Pair `environment:` claims with required reviewers or branch restrictions so the claim actually means something.

In short, OIDC gives you short-lived credentials scoped to a specific workflow, with no stored secrets to leak or rotate. That's why GitHub, AWS, Azure and GCP all recommend it for CI/CD deployments.
