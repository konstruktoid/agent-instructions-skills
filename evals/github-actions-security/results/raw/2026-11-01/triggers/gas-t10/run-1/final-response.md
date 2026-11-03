OIDC (OpenID Connect) is an identity layer built on OAuth 2.0. In CI/CD it lets a workflow prove who it is to a cloud provider at the moment it runs. The cloud then hands back credentials that expire within minutes or hours, so no stored secret is involved. I wrote this from general knowledge plus the skill's main guidance. Reading the skill's detailed OIDC reference file needed a permission I don't have yet, so I couldn't check against it.

## How it works (GitHub Actions example)

1. **Set up trust once.** In AWS, Azure, GCP or another provider, you register GitHub's OIDC issuer (`https://token.actions.githubusercontent.com`) as a trusted identity provider. You then create a role that only tokens with specific claims can take on.
2. **The job asks for a token.** A job with `permissions: id-token: write` asks GitHub for a signed JWT (JSON Web Token). The token describes the run with claims such as:
   - `sub`: for example `repo:my-org/my-repo:ref:refs/heads/main` or `repo:my-org/my-repo:environment:production`
   - `aud`: who the token is meant for, such as `sts.amazonaws.com`
   - `repository`, `ref`, `environment`, `job_workflow_ref`, `run_id`, and others
3. **The token is swapped for cloud credentials.** The cloud checks GitHub's signature and compares the claims to the role's trust policy. If they match, it issues short-lived credentials, for example through AWS STS `AssumeRoleWithWebIdentity`. Official actions like `aws-actions/configure-aws-credentials`, `azure/login` and `google-github-actions/auth` do this for you.
4. **The credentials expire on their own.** They usually last about an hour or less and only work for that one role.

## Why it's better than long-lived credentials

| | Stored static keys (e.g. an `AWS_ACCESS_KEY_ID` secret) | OIDC |
|---|---|---|
| **Secret at rest** | A key sits in repo or org secrets and can be leaked, copied or dumped by a compromised step | Nothing is stored. Each token is created for one run |
| **Lifetime** | Valid until someone rotates it, often months or years | Minutes to an hour, then useless |
| **Damage if leaked** | Works from anywhere until revoked | Short-lived and limited to one role |
| **Rotation** | Manual, often forgotten | None needed |
| **Who can use it** | Any workflow or job that can read the secret | Only runs whose claims match the trust policy (repo, branch, environment, workflow) |
| **Audit trail** | Cloud logs show the same key every time | Cloud logs show the role session, which can be traced to a specific repo and run |
| **Offboarding / sprawl** | Keys outlive the projects and people who made them | Trust is managed in one place on the cloud side |

The basic idea: a static key is something you *have*, and anyone holding it can use it. OIDC is based on something the run *is*, which the cloud checks each time.

## The catch: the trust condition does all the work

OIDC is only as strict as the trust policy. Common mistakes:

- **Wildcards in `sub`**, such as `repo:my-org/*` or `repo:my-org/my-repo:*`. These let any repo in the org, or any branch or pull request, take on the role. Match an **exact** `sub` instead (for example a protected branch or a named environment). Or match `job_workflow_ref` to pin the role to one specific reusable workflow.
- **Not checking `aud`.** Always restrict the audience.
- **Granting `id-token: write` at workflow level.** Grant it only to the job that deploys, and never to a job that runs untrusted code such as fork pull requests.
- **Over-privileged roles.** OIDC replaces the key, not least privilege. The role should still allow only what the deployment needs.
- **Not using environments.** Tying the `sub` to `environment:production` lets required reviewers and deployment protection rules control access to the cloud role.

## Minimal example

```yaml
permissions: {}

jobs:
  deploy:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    environment: production
    permissions:
      contents: read
      id-token: write   # needed to request the OIDC token
    steps:
      - uses: aws-actions/configure-aws-credentials@<full-commit-sha> # vX.Y.Z
        with:
          role-to-assume: arn:aws:iam::123456789012:role/deploy-prod
          aws-region: eu-north-1
```

The matching AWS trust policy condition:

```json
"Condition": {
  "StringEquals": {
    "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
    "token.actions.githubusercontent.com:sub": "repo:my-org/my-repo:environment:production"
  }
}
```

Replace `<full-commit-sha>` with the commit SHA of the action's current release, looked up at the time you add it, not taken from memory.

**When a static credential is still acceptable:** only when the target service doesn't support OIDC federation. Even then, scope the secret to an environment with required reviewers, keep its permissions minimal, rotate it on a schedule, and write the reason next to it in the workflow.
