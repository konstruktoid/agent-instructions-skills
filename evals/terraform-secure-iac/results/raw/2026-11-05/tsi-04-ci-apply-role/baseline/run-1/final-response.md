I added `ci_oidc.tf`. It passes `terraform fmt` and `terraform validate`, but I haven't run a plan or apply, so none of it has been exercised against AWS.

**What it creates**
- **OIDC provider:** `aws_iam_openid_connect_provider.github`, with audience `sts.amazonaws.com`.
- **Apply role (`ingest-ci-apply`):**
  - Only `repo:platform/ingest:ref:refs/heads/main` can assume it, so a pull request can't get apply credentials.
  - It can read and write the state object and its `.tflock` file.
  - It has full `s3:*`, `sqs:*` and `dynamodb:*` on the landing bucket, events queue and checkpoints table only, and no IAM permissions.
- **Plan role (`ingest-ci-plan`):**
  - I added this because the README says `plan` runs on pull requests, and those runs shouldn't get write access.
  - Only `repo:platform/ingest:pull_request` can assume it.
  - It can read the state and take the lock file, plus read-only describe/get calls on the three resources.
- **Outputs:** `ci_apply_role_arn` and `ci_plan_role_arn`, for the workflow's `role-to-assume`.

**What you need to check or do**
- **Bootstrap:** the roles live in the same state they manage, so someone must run the first `terraform apply` from a laptop. After that CI can take over.
- **Existing provider:** AWS allows only one GitHub OIDC provider per account. If this account already has one, import it as described in the comment in the file, or the apply will fail.
- **Workflow permissions:** the workflow needs `permissions: id-token: write`.
- **Environments:** if the apply job uses a GitHub `environment:`, the token's subject changes to `repo:platform/ingest:environment:<name>`. The apply trust condition would then need updating.
- **Plan role gaps:** the plan role's read list is hand-written. If a plan fails with an `AccessDenied`, add the missing read action.

I didn't commit anything.
