**OIDC (OpenID Connect)** is an identity layer built on OAuth 2.0. In CI/CD, and in GitHub Actions in particular, it lets a workflow prove who it is to a cloud provider without a stored secret. The cloud provider then gives it short-lived credentials in exchange.

## How it works (GitHub Actions → cloud)

1. **One-time trust setup.** In AWS, Azure or GCP, you register GitHub's OIDC issuer (`https://token.actions.githubusercontent.com`) as a trusted identity provider. You then create a role or identity whose trust policy says which workflows may use it. Conditions are written against token claims such as:
   - `sub`, e.g. `repo:my-org/my-repo:ref:refs/heads/main` or `repo:my-org/my-repo:environment:production`
   - `aud`, e.g. `sts.amazonaws.com`
   - and optionally `repository_owner`, `job_workflow_ref`, etc.
2. **At runtime** the job asks GitHub for a signed JWT (a signed token). The job needs `permissions: id-token: write` to do this.
3. The job sends that JWT to the cloud's token service, e.g. AWS STS `AssumeRoleWithWebIdentity`, Azure federated credentials, or GCP Workload Identity Federation.
4. The cloud checks the signature against GitHub's public keys and compares the claims to the trust policy. If they match, it returns **temporary credentials** that usually last 15 minutes to 1 hour.
5. The credentials expire on their own. Nothing is stored and nothing needs rotating.

```yaml
permissions:
  id-token: write   # allows requesting the OIDC JWT
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: aws-actions/configure-aws-credentials@<full-commit-sha> # vX.Y.Z
        with:
          role-to-assume: arn:aws:iam::123456789012:role/gha-deploy-prod
          aws-region: eu-north-1
```

## Why it beats long-lived credentials

| Concern | Long-lived keys (e.g. `AWS_ACCESS_KEY_ID` in secrets) | OIDC |
|---|---|---|
| **Lifetime** | Valid until someone rotates or revokes it, often months or years | Expires within minutes to an hour |
| **Damage if leaked** | A leaked key in logs, a fork, a compromised action or a cache works from anywhere until revoked | A stolen token expires quickly and the trust policy limits what it can do |
| **Rotation** | Manual, error-prone, often skipped | None needed: there is no stored secret |
| **Scope** | One key is often shared across repos, branches and environments | Trust can be limited to a specific repo, branch, tag, environment or reusable workflow |
| **Secret sprawl** | Copies sit in many repos and org secrets | No cloud secret is stored in GitHub at all |
| **Auditability** | Hard to tell which run used the key | Cloud logs record the role session, often with repo, run and workflow details from the claims |
| **Offboarding / incidents** | You have to find and revoke every copy | Change or delete the trust policy and access stops |

In short, OIDC replaces "something you have" (a static secret that can be copied) with "something you are" (a cryptographically checked workload identity). Credentials are created per run, last only briefly, and are tied to exact conditions.

## Pitfalls to avoid

- **Trust policy too broad.** A condition like `sub: repo:my-org/*`, a missing `sub` check, or only checking `aud` can let any repo, fork-triggered run or branch assume the role. Pin `sub` to specific repos and refs or environments.
- **Granting `id-token: write` everywhere.** Set it only on the jobs that need it, not at the workflow level for every job.
- **Untrusted triggers.** Don't hand OIDC-backed roles to workflows that run untrusted code, such as `pull_request_target` jobs that check out the PR's head.
- **Role permissions.** Still apply least privilege to the cloud role itself. Use separate roles for plan or read and for apply or deploy, and for each environment.
- **Environments.** Combine OIDC with GitHub Environments that require reviewers, and match `environment:` in the `sub` claim, so production credentials require an approved deployment.
