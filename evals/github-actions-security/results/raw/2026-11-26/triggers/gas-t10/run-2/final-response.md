**OIDC (OpenID Connect)** is an identity layer built on OAuth 2.0. An identity provider issues short-lived, signed tokens (JWTs) that make claims about who the bearer is. A relying party checks the signature against the provider's published keys and then decides whether to trust those claims.

## How it works for CI to cloud access

Take GitHub Actions to AWS, Azure or GCP as an example:

1. **One-time trust setup:** You register the CI platform as an identity provider in your cloud account. For GitHub that's `https://token.actions.githubusercontent.com`. Then you create a role whose trust policy only accepts tokens with specific claims, such as `repo:my-org/my-repo:ref:refs/heads/main` or `environment:production`.
2. **At run time:** The job asks the CI platform for an OIDC token. In GitHub Actions this needs `permissions: id-token: write`. The token is signed and lasts a few minutes. It contains claims like the repository, branch or tag, environment, workflow, and whether the run came from a pull request.
3. **Exchange:** The job sends that token to the cloud's security token service. For AWS that's `AssumeRoleWithWebIdentity`. The cloud checks the signature, audience and subject claims, then returns temporary credentials, usually valid for about an hour or less.
4. **Expiry:** The job uses the credentials, and they expire on their own.

## Why it's preferred over long-lived credentials

| Concern | Long-lived keys (e.g. `AWS_ACCESS_KEY_ID` in secrets) | OIDC federation |
|---|---|---|
| **Secret at rest** | A static secret sits in CI settings and can leak through logs, compromised actions, forks or exports | Nothing to store. No cloud secret exists in the CI platform |
| **Lifetime** | Valid until someone rotates it, often months or years | Minutes to about an hour. A leaked token soon becomes useless |
| **Rotation** | Manual, easy to forget, and can break things | Not needed. Every run gets fresh credentials |
| **Scope of trust** | Anyone holding the key is trusted, from anywhere | Trust is tied to verifiable context: which repo, branch, environment or workflow |
| **Blast radius** | One leaked key grants everything that key can do, until someone notices | An attacker would need to run code in the exact trusted context, and even then gets short-lived access |
| **Auditability** | Cloud logs only show "this key was used" | Cloud logs record the federated identity, such as repo, ref and run, so actions trace back to a specific workflow run |
| **Offboarding** | Keys must be found and revoked | Remove or narrow the trust policy and access ends |

## Caveats

OIDC moves the security boundary to the **trust policy**, so that policy has to be strict:

- **Pin the `sub` claim tightly.** Wildcards like `repo:my-org/*` or `repo:my-org/my-repo:*` let any branch, pull request or repo in the org assume the role. Prefer `environment:<name>` (with protection rules) or a specific protected ref.
- **Check the `aud` claim** (e.g. `sts.amazonaws.com`) so a token issued for another audience can't be replayed.
- **Only grant `id-token: write` to jobs that need it,** not workflow-wide. Be careful with triggers that run untrusted code with elevated context, such as `pull_request_target` or `workflow_run`.
- **Keep the cloud role least-privilege.** OIDC shortens how long credentials last, but it doesn't limit what they can do.
- **Consider custom claims.** GitHub supports customizing the subject template, for example to include `job_workflow_ref`, which pins access to a specific reusable workflow.

Overall, OIDC replaces a secret you have to protect with an identity that gets checked on every use. There's nothing long-lived to steal, and access is limited to the exact pipeline context you trust.
