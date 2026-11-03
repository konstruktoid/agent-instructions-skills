I added the GitHub OIDC provider and two IAM roles. `terraform fmt` and `terraform validate` pass. The scan still flags the three existing resources, and I haven't committed anything.

**Files added**
- **`ci_iam.tf`:** the OIDC provider and the two roles, each with a role policy.
- **`variables.tf`:** inputs for the repository, the apply branch and the state location.
- **`outputs.tf`:** the two role ARNs.

**Roles**
- **`ingest-ci-plan`:**
  - **Trust:** only `repo:platform/ingest:pull_request` can assume it.
  - **Permissions:** read-only on the bucket, queue and table, plus read on the state object.
  - **Lock:** it can write the single `.tflock` object that `use_lockfile` needs, and nothing else in the bucket.
- **`ingest-ci-apply`:**
  - **Trust:** only `repo:platform/ingest:ref:refs/heads/main` can assume it, so a PR or any other branch gets no write access.
  - **Permissions:** named read and write actions on those three resources and the state object. No wildcard actions.
- **Both roles:** sessions are limited to one hour, and neither has any IAM permissions, so CI can't widen its own access.

**Checks**
- **`terraform fmt`:** clean.
- **`terraform init -backend=false` and `terraform validate`:** both pass. I ran them in a temporary copy, so no `.terraform/` directory was left in the repo.
- **`tflint`:** not installed here, so it didn't run.
- **Plan:** I didn't run one because there are no AWS credentials in this environment.
- **checkov:** the only scanner available. It fails 10 checks, all on `aws_s3_bucket.landing`, `aws_sqs_queue.events` and `aws_dynamodb_table.checkpoints` in `main.tf`. None are in the new IAM code. The S3 failures include versioning, public access block, KMS encryption and logging. I left them alone because fixing them changes your infrastructure and is outside this request.

**Before you rely on it**
1. **First apply:** this has to be run once from a laptop or an admin identity. CI can't create the roles it will assume.
2. **Existing provider:** an AWS account allows only one OIDC provider for `token.actions.githubusercontent.com`. If one already exists, import it with `terraform import aws_iam_openid_connect_provider.github <arn>` or switch to a data source.
3. **State bucket:** the backend block can't take variables, so `state_bucket_name` and `state_key` must be kept in step with `versions.tf` by hand.
4. **Workflow:** the `platform/ingest` workflow needs `permissions: id-token: write` and `aws-actions/configure-aws-credentials` with the matching role ARN in each job. Pin the actions by commit SHA.
5. **Stricter gate:** if you want a manual approval before apply, add a GitHub Environment and change the apply subject to `repo:platform/ingest:environment:<name>`.
6. **Permission gaps:** the action lists are my best estimate for provider v6 refresh. A plan that fails with `AccessDenied` should be fixed by adding the missing named action, not by widening to a wildcard.
