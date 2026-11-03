# OIDC and long-lived cloud credentials

## What OIDC is

**OpenID Connect (OIDC)** is an identity layer built on OAuth 2.0. An **identity provider** issues a signed **JSON Web Token (JWT)** that says who the bearer is. Anyone with the provider's public keys can check that token.

In CI/CD, this is used for **workload identity federation**. Using GitHub Actions as an example:

1. A workflow job asks GitHub's OIDC provider (`https://token.actions.githubusercontent.com`) for an ID token. It can only do this if the job has `permissions: id-token: write`.
2. GitHub issues a short-lived JWT. Its claims describe the run, for example:
   - `sub`: `repo:my-org/my-repo:ref:refs/heads/main` or `repo:my-org/my-repo:environment:prod`
   - `repository`, `ref`, `environment`, `workflow_ref`, `job_workflow_ref`, `actor`, `event_name`
   - `aud`: the intended audience, such as `sts.amazonaws.com`
3. The job sends that JWT to the cloud provider (AWS STS `AssumeRoleWithWebIdentity`, Azure federated credentials, GCP Workload Identity Federation, and so on).
4. The cloud provider checks the signature and compares the claims against a **trust policy** you wrote. If they match, it returns **temporary cloud credentials**, usually valid for minutes to an hour.

The repository never stores a cloud secret. Trust is set up once between the cloud account and the identity provider, and each run gets fresh credentials.

```yaml
permissions:
  id-token: write   # allow the job to request an OIDC token
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: prod
    steps:
      - uses: aws-actions/configure-aws-credentials@<pinned-sha>  # vX.Y.Z
        with:
          role-to-assume: arn:aws:iam::123456789012:role/deploy-prod
          aws-region: eu-north-1
```

## Why it's preferred over long-lived credentials

| Concern | Long-lived keys (e.g. `AWS_ACCESS_KEY_ID` in secrets) | OIDC |
|---|---|---|
| **Lifetime** | Valid until someone rotates or revokes them, often for months or years | Expires in minutes to an hour |
| **Blast radius if leaked** | Works from anywhere until revoked | Short-lived and limited to one role. The token is also tied to an audience. |
| **Rotation** | Manual, easy to forget, and can cause outages | Not needed, since every run gets new credentials |
| **Storage** | Secrets in repos or orgs that can be copied, logged or exfiltrated | No cloud secret stored in CI |
| **Scoping** | Anyone who can read the secret can use it in any workflow, branch or fork context that has access | The trust policy can limit access to a specific repo, branch, environment, tag or reusable workflow |
| **Auditability** | Activity shows up as one static key, which is hard to link to a run | Cloud audit logs show the role session, and claims can be tied to a specific repo and run |
| **Offboarding / sprawl** | Keys get copied into many places and outlive the projects that used them | Removing the trust relationship cuts off access immediately |

In short, long-lived keys are **bearer secrets**: anyone holding one is authorized. OIDC replaces them with **short-lived credentials** that are issued only after the cloud provider checks where the request came from.

## Pitfalls to avoid

OIDC is only as strong as the trust policy:

- **Always constrain `sub`, and `aud` too.** A policy that only checks the issuer, or uses wildcards like `repo:my-org/*`, lets any repo in the org (or worse) assume the role.
- **Bind production roles to a protected `environment`** (`sub: repo:org/repo:environment:prod`) rather than just a branch. Environments can require reviewers and limit which branches can deploy.
- **Grant `id-token: write` only to the jobs that need it**, not to the whole workflow.
- **Be careful with `pull_request_target` and `workflow_run`.** These triggers run with base-repo privileges, so if they run untrusted code from a pull request, that code could get a token and assume your role.
- **Use one role per purpose with least-privilege policies.** A short-lived admin credential is still an admin credential.
- **For shared deploy logic,** constrain `job_workflow_ref` so only your approved reusable workflow can assume the role.
