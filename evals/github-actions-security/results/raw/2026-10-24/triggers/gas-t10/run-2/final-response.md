## What OIDC is

**OpenID Connect (OIDC)** is an identity layer on top of OAuth 2.0. One party, the *identity provider*, issues a signed JSON Web Token (JWT) that says who the bearer is. Another party, the *relying party*, checks that token against the provider's public keys and decides whether to trust it.

In CI/CD, and GitHub Actions in particular:

1. **GitHub is the identity provider.** When a job has `permissions: id-token: write`, it can ask GitHub for a short-lived OIDC token. The token's claims describe the run, for example:
   - `sub`: `repo:my-org/my-repo:ref:refs/heads/main` or `repo:my-org/my-repo:environment:production`
   - `repository`, `ref`, `environment`, `workflow_ref`, `job_workflow_ref`, `actor`, `event_name`
   - `aud`: the intended audience, such as `sts.amazonaws.com`
2. **The cloud provider is the relying party.** You register GitHub (`https://token.actions.githubusercontent.com`) as a trusted identity provider in AWS IAM, Azure Entra ID, GCP Workload Identity Federation or HashiCorp Vault. You also create a role or trust policy that only accepts tokens whose claims match, such as "only `my-org/my-repo` on `main`" or "only the `production` environment".
3. **Token exchange.** The workflow sends the GitHub token to the cloud's security token service (for example, `sts:AssumeRoleWithWebIdentity`). The cloud checks the signature and claims, then returns temporary cloud credentials that usually last 15 to 60 minutes.

```yaml
permissions:
  id-token: write   # allow requesting the OIDC token
  contents: read

steps:
  - uses: aws-actions/configure-aws-credentials@<sha>  # pin to a commit SHA
    with:
      role-to-assume: arn:aws:iam::123456789012:role/deploy-prod
      aws-region: eu-north-1
```

No cloud secret is stored anywhere in GitHub.

## Why it's preferred over long-lived credentials

| Concern | Long-lived keys (e.g. `AWS_ACCESS_KEY_ID` in secrets) | OIDC federation |
|---|---|---|
| **Secret at rest** | A static key sits in repo or org secrets and can leak through logs, forks, compromised actions or exported settings | Nothing to store; the token is minted for each job |
| **Lifetime if leaked** | Valid until someone notices and rotates it, often months | Expires in minutes; the GitHub JWT itself in about 5–10 minutes |
| **Rotation** | Manual and error-prone, so often skipped | Not needed |
| **Scope of trust** | Anyone who holds the key gets full access, from anywhere | Trust is tied to claims: a specific repo, branch, environment or reusable workflow |
| **Blast radius from a compromised workflow** | An attacker can take the key elsewhere and keep using it | An attacker only gets short-lived credentials, and only from a context that matches the trust policy |
| **Auditability** | Cloud logs show "key X was used" | Cloud logs record the role session, which you can tag with repo or run details, so you can trace activity back to a specific workflow run |
| **Environment gating** | Hard to enforce | Combine `environment:` in the `sub` claim with GitHub environment protection rules (required reviewers, branch restrictions), so production credentials can't be issued without approval |

## Pitfalls that weaken OIDC

- **Overly broad trust policies.** Matching `sub` with `repo:my-org/*` or just `*` lets any repo, branch or pull request assume the role. Always pin the repository, and ideally the branch or environment as well.
- **Not checking `aud`.** Make sure the audience matches what your cloud expects.
- **Untrusted triggers.** If a role can be assumed from `pull_request_target` or other contexts that handle fork code, an attacker's code could get cloud credentials. Limit trust to protected refs or environments.
- **Granting `id-token: write` too widely.** Grant it only to the job that needs it, not to the whole workflow.
- **Reusable workflows.** When a central deploy workflow does the work, use the `job_workflow_ref` claim to restrict trust to it.

**In short:** OIDC swaps a stored, long-lived, broadly usable secret for a short-lived credential that is tied to a specific identity and context, and is issued only when needed. That removes the most common way CI pipelines leak cloud credentials.
