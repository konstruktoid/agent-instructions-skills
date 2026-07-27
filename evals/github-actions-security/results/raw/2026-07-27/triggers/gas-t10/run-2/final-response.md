OIDC (OpenID Connect) is an identity layer on top of OAuth 2.0 that lets one system prove "who it is" to another using short-lived, cryptographically signed tokens instead of a shared secret.

**How it works in CI/CD (e.g., GitHub Actions → AWS/GCP/Azure):**
1. During a workflow run, GitHub's OIDC provider issues a signed JSON Web Token (JWT) containing claims like repo, branch, workflow, and actor.
2. The cloud provider (AWS IAM, GCP Workload Identity Federation, Azure AD) is configured to trust GitHub's OIDC issuer and to check specific claims (e.g., "only accept tokens where `repo == org/myrepo` and `ref == refs/heads/main`").
3. If the token matches the trust policy, the cloud provider hands back temporary credentials (usually valid for minutes to an hour).
4. The workflow uses those temporary credentials, which then expire on their own.

**Why it's preferred over long-lived credentials (static access keys/secrets):**

- **No secret to steal.** There's no long-lived `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY` sitting in GitHub Secrets that can leak via a misconfigured log, a compromised dependency, or a malicious PR. The token is generated fresh per run and expires quickly.
- **Narrow, verifiable trust.** The trust policy binds credentials to specific claims (repo, branch, environment, even specific workflow file), so a token minted for one repo/branch can't be replayed to access another.
- **No rotation burden.** Static keys need manual/scripted rotation and tend to go stale or get over-permissioned over time. OIDC tokens are always fresh and short-lived by design.
- **Better audit trail.** Cloud-side logs show exactly which repo/workflow/run assumed the role, rather than "some process using key XYZ."
- **Reduced blast radius.** Even if a workflow run is compromised, the attacker only gets a token valid for that run's duration and scope, not a durable credential usable indefinitely from anywhere.

In short: OIDC replaces "a secret you must protect forever" with "a fact you can prove right now," which eliminates an entire class of credential-leak and stale-permission risks — this is why the `github-actions-security` skill's hardening guidance treats OIDC + cloud IAM roles as the preferred pattern over storing static cloud credentials in repo/org secrets.
