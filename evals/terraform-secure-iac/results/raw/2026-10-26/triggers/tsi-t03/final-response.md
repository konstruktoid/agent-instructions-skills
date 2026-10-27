I can't review the pipeline's IAM role because it isn't in this repository, so I haven't signed off on anything. I also couldn't read the skill's `execution-identity.md` reference, because the read was denied. This review is based only on the repo files, not on that reference.

**What I searched for.** I looked for `aws_iam_*` resources, a trust policy or `assume_role`, `role-to-assume`, an OIDC provider, and credentials set in CI. The search found none of them. The role is probably defined in another repo, in a bootstrap or account-baseline stack, or in the console.

**What the repo contains.** The only Terraform is `infra/main.tf`, a single security group. There's no provider block, backend, lock file, or `.tflint.hcl`. I didn't run `fmt`, `validate`, or `tflint`, because there's nothing to configure them against.

**Findings that bear on the production apply:**

1. **The workflow gives the pipeline broad permissions.** `.github/workflows/deploy.yml:7` sets `permissions: write-all` on a `pull_request` trigger. If this workflow ever assumes your Terraform role through OIDC, any PR could use that identity. Set `permissions: contents: read` and add `id-token: write` only on the job that needs it.
2. **Expression injection.** `deploy.yml:14` puts `${{ github.event.pull_request.title }}` straight into a shell command. A crafted PR title can run commands in the job. Pass it through an `env:` variable instead.
3. **Open SSH in `main.tf:8`.** The `bastion` security group allows port 22 from `0.0.0.0/0`. Restrict the CIDR before applying this to production.
4. **No apply gate.** The workflow doesn't run `plan` or `apply`, so I can't tell whether plan and apply use separate identities or whether production apply needs an approval.

**What I need to review the role itself:**
- The role's trust policy and its attached or inline permission policies. Paste the JSON, or point me to the repo that defines it.
- The workflow or pipeline that assumes it. In particular, I'd check how the OIDC `sub` claim is scoped (repo, branch, environment) and whether a PR can assume it.

With those I can check the role against least privilege, a read-only plan role separate from the apply role, short-lived credentials, and a trust policy that only your production branch or environment can assume.
