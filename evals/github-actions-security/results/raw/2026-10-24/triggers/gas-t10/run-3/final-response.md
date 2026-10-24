# OIDC and why it beats long-lived cloud credentials

## What OIDC is

**OpenID Connect (OIDC)** is an identity layer on top of OAuth 2.0. One system (the *identity provider*) issues a signed **JSON Web Token (JWT)** that says who or what the bearer is. Another system (the *relying party*) checks the signature against the provider's public keys and trusts the claims inside.

In CI/CD, and especially GitHub Actions, it works like this:

1. A workflow job asks GitHub's OIDC provider (`https://token.actions.githubusercontent.com`) for a token. The job needs `permissions: id-token: write` to do this.
2. GitHub issues a short-lived JWT. Its claims describe the job, for example:
   - `sub`: `repo:my-org/my-repo:ref:refs/heads/main` or `repo:my-org/my-repo:environment:production`
   - `repository`, `ref`, `environment`, `workflow`, `job_workflow_ref`, `actor`, `event_name`, and others
   - `aud`: the intended audience, such as `sts.amazonaws.com`
3. The job sends that JWT to the cloud provider's token exchange: AWS STS `AssumeRoleWithWebIdentity`, Azure federated credentials, or GCP Workload Identity Federation.
4. The cloud provider checks the signature and compares the claims to a **trust policy** you set up ahead of time, for example "only `my-org/my-repo` on `main`".
5. If the claims match, the cloud returns **temporary credentials**. These usually expire in about 15 minutes to 1 hour and are scoped to one role.

No cloud secret is ever stored in GitHub.

## Why it's preferred over long-lived credentials

| Concern | Long-lived keys (e.g. `AWS_ACCESS_KEY_ID` in secrets) | OIDC federation |
|---|---|---|
| **Lifetime** | Valid until someone rotates them, often months or years | Expire within minutes to an hour |
| **Storage** | A static secret sits in the repo or org settings, where it can be exfiltrated | Nothing to store; the token is minted per job |
| **Blast radius if leaked** | Usable from anywhere, by anyone, until revoked | A leaked token is near-useless soon after; the audience is bound and lifetime is short |
| **Scoping** | One key is often shared across repos, branches and environments | The trust policy can pin repo, branch, environment, workflow or event |
| **Rotation** | Manual, error-prone and often neglected | Not needed |
| **Auditability** | Cloud logs show "key X was used" | Cloud logs show the role session, and the token claims tie it to a specific repo and run |
| **Offboarding / sprawl** | Keys outlive the people and projects that created them | Delete the trust relationship and access ends |

The core security argument is that **a credential that doesn't exist can't be stolen**. Long-lived keys are among the most common things attackers grab from CI: through a malicious dependency, a compromised third-party action, a `pull_request_target` misconfiguration, or a secret printed into logs. OIDC shrinks both the window and the scope of any compromise.

## Minimal GitHub Actions example (AWS)

```yaml
permissions:
  contents: read
  id-token: write   # needed to request the OIDC token

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: aws-actions/configure-aws-credentials@<full-commit-sha>  # pin by SHA
        with:
          role-to-assume: arn:aws:iam::123456789012:role/gha-deploy-prod
          aws-region: eu-north-1
```

Here is the matching IAM trust policy condition. This is the part that actually enforces security:

```json
"Condition": {
  "StringEquals": {
    "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
    "token.actions.githubusercontent.com:sub": "repo:my-org/my-repo:environment:production"
  }
}
```

## Pitfalls that weaken OIDC

- **Loose `sub` matching.** Patterns like `repo:my-org/*` or `repo:my-org/my-repo:*` let any branch, any pull request, or any repo in the org assume the role. Pin to a specific repo plus a branch or environment.
- **Not checking `aud`.** Always require the expected audience.
- **Granting `id-token: write` too widely.** Give it only to jobs that need cloud access, not at workflow level for every job.
- **Untrusted triggers.** Don't let jobs that run untrusted pull request code reach a role with deploy permissions. Use environments with protection rules for production roles.
- **Over-privileged roles.** OIDC fixes *how* you authenticate. The role itself still has to follow least privilege.
- **Reusable workflows.** For tighter binding, use the `job_workflow_ref` claim, or a customized `sub` claim, so only a specific vetted workflow can assume the role.

**In short:** OIDC replaces "store a permanent password for the cloud in CI" with "CI proves who it is on each run and gets a short-lived, narrowly scoped credential." That removes secret storage and manual rotation, and greatly limits the damage from a leak.
