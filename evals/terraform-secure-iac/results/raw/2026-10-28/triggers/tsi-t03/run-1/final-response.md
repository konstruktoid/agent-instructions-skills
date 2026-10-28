I couldn't review the pipeline's IAM role because it isn't in this repository. Nothing here defines it: there's no `aws_iam_role` or policy, no OIDC trust policy, and no workflow step that assumes a role. A search for `iam`, `role`, `assume`, `terraform`, `aws_` and `oidc` turned up only one resource, the security group in `infra/main.tf`.

What the repo does contain:

| File | Contents |
|---|---|
| `infra/main.tf` | A single `aws_security_group "bastion"`, with no provider, backend or IAM |
| `.github/workflows/deploy.yml` | No Terraform steps and no AWS credentials; it checks out the code and echoes the PR title |
| `.gitlab-ci.yml` | `npm ci` and `npm run build` only |

**Problems I found while looking, which you should fix before any production apply:**

1. **`.github/workflows/deploy.yml:7`: `permissions: write-all` on a `pull_request` trigger.** Every PR run gets a write-scoped `GITHUB_TOKEN`. If this workflow later gets AWS role assumption, PR-triggered runs could reach production credentials. Set `permissions: contents: read` at the top level, and grant `id-token: write` only to a separate apply job. That job should run on `push` to `main` behind a protected GitHub environment, not on `pull_request`.
2. **`.github/workflows/deploy.yml:14`: script injection.** `${{ github.event.pull_request.title }}` is placed directly into a shell `run:` line. Anyone who opens a PR can choose the title and so run commands on the runner, with the write-all token from point 1. Pass it in through `env:` (for example `TITLE: ${{ github.event.pull_request.title }}`) and use `"$TITLE"`.
3. **`infra/main.tf:8`: SSH (port 22) is open to `0.0.0.0/0`.** Limit it to known CIDRs, or remove the bastion and use SSM Session Manager.
4. **`infra/main.tf`: no `terraform` block.** There's no `required_providers` pin, no backend and no `.terraform.lock.hcl`. Production state would therefore end up wherever whoever runs the apply happens to run it.

**What to check once you have the role's definition:**
- **Trust policy:** it should trust GitHub OIDC (`token.actions.githubusercontent.com`), with `aud` set to `sts.amazonaws.com`. `sub` should be pinned to `repo:<org>/<repo>:environment:production` or a specific ref, not `repo:<org>/*` or `*`. There should be no long-lived access keys.
- **Separate roles:** a read-only role for `plan` on PRs, and the write role only for the protected `apply` job.
- **Permissions:** limited to the services and resource ARNs this configuration manages (right now that's EC2 security groups), plus access to the state bucket and lock table. It shouldn't have `AdministratorAccess`, `*:*`, or `iam:*` / `iam:PassRole` on `*`.
- **Limits:** a short `max_session_duration`, and a permissions boundary if the role creates IAM objects.

**What I didn't do:**
- I didn't run `terraform fmt`, `validate` or `tflint`. I had no shell tool in this session, and with no IAM code there was nothing for them to check on this question.
- I couldn't open the skill's `execution-identity.md` reference because permission to read it was denied. The checklist above comes from the skill's own summary checklist and standard AWS OIDC practice.

If the role lives in another repo, an AWS account-bootstrap stack or the console, send me the trust policy and the attached policies (or where to find them) and I'll review them against this list. Points 1 and 2 are worth fixing now regardless.
