I can't review the pipeline's IAM role because this repository doesn't define one. Before you let anything apply to production, you'll need to point me to where that role lives.

## What I checked

I searched the whole workspace for `terraform`, `assume`, `role_arn`, `iam`, `aws_` and `credentials`. The only hit is one resource in `infra/main.tf`:

- There is no `aws_iam_role`, `aws_iam_policy`, trust policy, or `assume_role` provider block.
- No CI file runs `terraform plan` or `apply`. `.github/workflows/deploy.yml` only echoes the PR title. `.gitlab-ci.yml` and `Jenkinsfile` don't mention Terraform or AWS at all.
- There is no `provider` block, `backend`, or `.terraform.lock.hcl` either.

So the role your pipeline assumes is defined somewhere else: another repo, an account bootstrap stack, or the CI platform's settings.

## Problems I did find that affect a production apply

1. **`.github/workflows/deploy.yml:7`: `permissions: write-all` on a `pull_request` trigger.** Every PR gets a token that can write to the repository. Once someone adds AWS OIDC federation to this workflow, it will also be able to request `id-token: write`. That means any PR could get a cloud identity. Set `permissions: contents: read` at the top level. Grant `id-token: write` only to the job that needs it, and only on protected-branch or environment-gated runs, never on `pull_request`.
2. **`.github/workflows/deploy.yml:14`: script injection.** `${{ github.event.pull_request.title }}` is pasted straight into a `run:` shell command. Anyone who can open a PR can choose a title that runs commands on the runner, which has the write-all token. Pass the title through an `env:` variable and quote it as `"$TITLE"`.
3. **`infra/main.tf:8`: SSH (port 22) open to `0.0.0.0/0`.** This is the bastion security group, and it accepts SSH from anywhere on the internet. Restrict it to known CIDRs, or replace SSH with SSM Session Manager.

## What to check once you show me the role

- **Trust policy:** the OIDC `sub` condition should be pinned to one repo and a protected branch or environment (for example `repo:<org>/<repo>:environment:production`), not `repo:<org>/*` or `pull_request`. `aud` should be `sts.amazonaws.com`.
- **Separate plan and apply roles:** plan uses read-only credentials and apply uses write credentials, and only the gated apply job can assume the write role.
- **Permissions:** limited to the services and resources the configuration actually manages. No `AdministratorAccess`, no `*:*`, and no `iam:*` or `iam:PassRole` on `*`. Add a permissions boundary if the role can create IAM objects.
- **Credentials:** short-lived (OIDC/STS with a modest `max_session_duration`), with no static access keys stored in CI secrets.
- **State access:** the role can read and write only this stack's state key and its lock.

## Caveats

- I couldn't read the skill's `execution-identity.md` reference because the read permission wasn't granted. The checklist above comes from the skill's summary checklist and general practice.
- I didn't run `terraform fmt`, `validate`, `tflint` or any scanner. There's no shell tool in this session, and with no provider or backend configured, validating would show nothing about the role.

Send me the path or repo where the role and its trust policy are defined, or the workflow that actually runs `terraform apply`, and I'll review it against the list above.
