# OIDC and why it beats long-lived cloud credentials

## What OIDC is

OpenID Connect (OIDC) is an identity layer on top of OAuth 2.0. It lets one system prove who it is to another by presenting a **signed token** (a JWT) issued by a trusted identity provider.

In CI/CD, such as GitHub Actions, GitLab CI, or CircleCI, the flow works like this:

1. **Trust setup (once).** In your cloud account (AWS, GCP, Azure, and others), you register the CI provider as a trusted identity provider. You also create a role or service account. Its trust policy says which token claims are allowed to assume it. For example: `repo:my-org/my-repo`, `ref:refs/heads/main`, or `environment:production`.
2. **Token issuance (every run).** When a job starts, the CI provider mints a short-lived JWT for that specific run. The JWT is signed with the provider's private key. It carries claims such as the repository, branch, workflow, environment, and an audience (`aud`).
3. **Token exchange.** The job sends the JWT to the cloud's security token service. The cloud does the following:
   - It verifies the signature against the provider's published public keys (JWKS).
   - It checks that the claims match the trust policy.
   - If they match, it returns **temporary credentials**, usually valid for minutes to an hour.
4. **Use and expiry.** The job uses those credentials, which then expire on their own.

In GitHub Actions, this requires the `id-token: write` permission on the job. Without it, no token can be requested.

## Why it is preferred over long-lived credentials

| Concern | Long-lived keys (stored as secrets) | OIDC |
|---|---|---|
| **Secret to steal** | A static access key or service-account JSON sits in the CI secret store indefinitely. | Nothing durable is stored. The token exists only for the run. |
| **Blast radius of a leak** | A leaked key works from anywhere until someone notices and revokes it. | Credentials expire in minutes. The token is also bound to an audience and to specific claims. |
| **Rotation** | Manual and easy to neglect. Keys often live for years. | Automatic, because every run gets fresh credentials. |
| **Scoping** | Typically one key shared across many repos and branches. | Trust can be limited to a specific repo, branch, environment, or workflow. A fork or feature branch can be denied production access. |
| **Auditability** | CloudTrail or audit logs show "the CI key" did something. | Sessions can be traced to a repo, run, and commit via the claims. |
| **Operational burden** | You have to create, distribute, rotate, and revoke keys, and answer for them in audits. | You maintain one trust policy per role. |

The core point is that long-lived credentials are **bearer secrets**. Anyone who obtains one can use it. They can obtain it through a compromised third-party action, a log leak, a malicious pull request, or a breach of the CI secret store. OIDC replaces a stored secret with a short-lived, identity-bound proof that is checked against policy at the moment of use.

## Caveats

- **The trust policy is the security boundary.** A sloppy `sub` condition, such as a wildcard that matches every repo in an org or every branch, can let unintended workflows assume your role. Pin the conditions as tightly as practical.
- **Grant `id-token: write` only to the jobs that need it.** Any code in that job, including third-party actions, can request a token.
- **Least privilege still applies.** The role you assume should have only the permissions the job needs.
- **Not every target supports it.** Some SaaS services and registries still require static tokens. For those, use narrowly scoped, short-lived tokens where possible.

If you want, I can look at a specific workflow in this repo and check its OIDC setup and trust conditions.
