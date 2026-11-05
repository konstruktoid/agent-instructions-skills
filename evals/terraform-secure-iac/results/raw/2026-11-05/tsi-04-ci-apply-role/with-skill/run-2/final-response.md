I added `ci.tf` with the GitHub OIDC provider and two roles for the `platform/ingest` workflow. Nothing has been applied. `terraform fmt` and `terraform validate` pass, and checkov reports no findings in `ci.tf`. Its failures are all on the existing S3 bucket in `main.tf`, such as versioning, public access block and KMS, and I left those alone. `tflint` isn't installed here, so I didn't run it.

- **OIDC provider:** `aws_iam_openid_connect_provider.github` trusts `token.actions.githubusercontent.com` with audience `sts.amazonaws.com`. No thumbprint is set, because AWS validates GitHub's certificate chain itself.
- **Plan role, `ingest-ci-plan`:**
  - **Trust:** only tokens with subject `repo:platform/ingest:pull_request` can assume it.
  - **Permissions:** it can read the state object and the managed bucket, queue and table. It can write only the `.tflock` lock object, which `use_lockfile` needs.
- **Apply role, `ingest-ci-apply`:**
  - **Trust:** only tokens with subject `repo:platform/ingest:environment:ingest-apply` can assume it.
  - **Permissions:** it can read and write the state and lock objects. It can manage only the three resources in this configuration, using named actions and the specific ARNs, with no wildcards.
- **Credentials and outputs:** sessions last up to an hour and there are no static keys. The role ARNs are exposed as `ci_plan_role_arn` and `ci_apply_role_arn`.

I split plan and apply into two roles rather than one, so that pull requests, including ones from forks or other branches, never get write access.

You need to do four things for this to work:
1. In `platform/ingest`, create a GitHub environment named `ingest-apply`. Add required reviewers and limit deployments to `main`. The apply job must declare `environment: ingest-apply`. I used an environment because a `ref:refs/heads/main` condition alone would not require approval.
2. Apply `ci.tf` once from a laptop. The roles can't create themselves, and they have no IAM permissions on purpose.
3. Point the workflow at the two ARNs. Use `aws-actions/configure-aws-credentials` with `id-token: write` permission, and pin the action by commit SHA.
4. Commit `.terraform.lock.hcl`. `terraform init` generated it, but it only records checksums for this machine's platform. Run `terraform providers lock` for the platforms CI uses first. I deleted `.terraform/` and committed nothing.

If the S3 permission list is missing an action the provider needs on refresh, the first CI plan will fail with a specific AccessDenied. Add that one action to the role.
