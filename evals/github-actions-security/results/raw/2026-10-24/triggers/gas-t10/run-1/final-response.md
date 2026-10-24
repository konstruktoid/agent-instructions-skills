# OpenID Connect (OIDC) and short-lived cloud credentials

## What OIDC is

**OpenID Connect (OIDC)** is an identity layer built on OAuth 2.0. An **identity provider (IdP)** issues signed **JSON Web Tokens (JWTs)** that say who or what the holder is. A relying party checks the token's signature against the IdP's published public keys (JWKS) and then trusts the claims inside it.

In CI/CD, the CI platform acts as the IdP. GitHub Actions is the usual example. Each workflow job can ask for an OIDC token signed by `https://token.actions.githubusercontent.com`. The token has claims that describe the run, for example:

| Claim | Example |
|---|---|
| `iss` | `https://token.actions.githubusercontent.com` |
| `aud` | `sts.amazonaws.com` (whoever the token is meant for) |
| `sub` | `repo:my-org/my-repo:ref:refs/heads/main` or `repo:my-org/my-repo:environment:prod` |
| `repository`, `ref`, `workflow_ref`, `job_workflow_ref`, `environment`, `actor`, `run_id`, … | Details about the run |

## How the exchange works

1. **One-time setup:** in AWS, Azure, or GCP you register GitHub as a trusted OIDC provider. You also create a role (or workload identity) with a **trust policy**, for example: "allow only tokens where `sub` = `repo:my-org/my-repo:environment:prod` and `aud` = `sts.amazonaws.com`."
2. **At runtime:** the job asks GitHub for an OIDC token. The job needs `permissions: id-token: write` to do this.
3. The job sends that token to the cloud's security token service, such as AWS `AssumeRoleWithWebIdentity`, Azure federated credentials, or GCP Workload Identity Federation.
4. The cloud checks the signature and the claims against the trust policy. If they match, it returns **short-lived credentials**, usually valid for about 15 minutes to 1 hour.

```yaml
permissions:
  id-token: write   # allow requesting the OIDC JWT
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: prod
    steps:
      - uses: aws-actions/configure-aws-credentials@<full-commit-sha> # vX.Y.Z
        with:
          role-to-assume: arn:aws:iam::123456789012:role/gha-deploy-prod
          aws-region: eu-north-1
```

In a real workflow, pin the action to a full commit SHA from its latest release. Don't use a floating tag.

## Why it beats long-lived credentials

| Long-lived secrets (e.g. `AWS_ACCESS_KEY_ID` in repo secrets) | OIDC federation |
|---|---|
| A static secret is stored in GitHub, so there's something to steal | **No stored cloud secret.** Nothing to leak from settings, forks, or backups |
| Valid for months or years until someone rotates it | Credentials **expire on their own** within minutes or hours |
| A leaked key works from anywhere, until someone notices | A stolen token is short-lived and useful only within its narrow scope |
| Manual rotation work, often skipped | **No rotation needed** |
| Any workflow, branch, or job that can read the secret can use it | Access is **limited by claims**: a specific repo, branch, environment, or reusable workflow |
| Hard to tell which run did what | Cloud audit logs link each session to the role session and token claims, so you can trace activity back to a specific run |
| Often one broad key is shared everywhere | Encourages **one narrow role per purpose**, such as separate read-only CI and prod-deploy roles |

In short, OIDC swaps a long-lived shared secret for a short-lived identity that the cloud checks on every run. Leaking a static key gives an attacker standing access. A leaked OIDC token is short-lived and narrowly scoped, and it can be unusable outright if the trust policy is tight.

## Pitfalls to avoid

- **Overly broad trust policies.** Wildcards like `repo:my-org/*` or `repo:my-org/my-repo:*` let any branch, PR, or repo in the org assume the role. Pin `sub` to a specific branch or, better, a protected **environment**. Always check `aud` too.
- **Granting `id-token: write` workflow-wide.** Grant it only to the job that needs it, and don't grant it to jobs that run untrusted code, such as `pull_request_target` or `workflow_run` jobs that check out PR code.
- **Over-privileged roles.** OIDC fixes how credentials are delivered, not what they allow. Keep the cloud role least-privilege.
- **Unprotected environments.** If `sub` is tied to `environment:prod`, add required reviewers and branch restrictions to that environment. Otherwise anyone who can push a workflow can get prod credentials.
- **Reusable workflows.** Consider customizing the `sub` claim or matching on `job_workflow_ref`, so that only your approved deploy workflow can assume the role.

If you want, I can review existing workflows or cloud trust policies for these issues.
