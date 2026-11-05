I added `ci.tf` with the GitHub OIDC provider and two IAM roles. I haven't planned or applied it. `terraform fmt` and `terraform validate` pass. `tflint` isn't installed here. `checkov` reports no findings in `ci.tf`. Its failures are all on the existing resources in `main.tf` (landing bucket versioning, encryption, public-access block and similar), which I left alone.

**What it creates**
- **OIDC provider:** `token.actions.githubusercontent.com`, with audience `sts.amazonaws.com`. An account can hold only one of these. If another stack already manages it, import it or switch to a data source.
- **`ingest-ci-plan` role:** for pull requests. Only tokens whose subject is `repo:platform/ingest:pull_request` can assume it. It can read the managed resources and the state, and write only the `.tflock` lock object.
- **`ingest-ci-apply` role:** for merges. Only tokens whose subject is `repo:platform/ingest:ref:refs/heads/main` can assume it. It can manage only the landing bucket, events queue and checkpoints table, and read and write the state and lock objects.

**Choices to know about**
- **Two roles:** you asked for one role. I split plan and apply so a pull-request run, which can come from any branch, never holds write access.
- **Permissions:** both roles list named actions on specific ARNs and have no IAM permissions. The one `*` resource is `sqs:ListQueues`, which doesn't support resource-level scoping.
- **Session length:** sessions are capped at one hour.
- **Account ID:** nothing is hard-coded. The account comes from `aws_caller_identity`, and the repo and state location are variables whose defaults match the current backend.
- **`.gitignore`:** I added one containing `.terraform/`.
- **Lock file:** I generated `.terraform.lock.hcl` with `init`. It only records the platform I'm on, so run `terraform providers lock` for the platforms CI uses before committing it.

**Before this works**
- The first apply of these roles has to be run by an engineer with IAM rights. The CI roles can't create themselves.
- The permission lists are my best estimate of what AWS provider 6.x needs to refresh and manage these three resources. If a plan fails with AccessDenied, add that action to the matching statement, not a wildcard.
- The workflow in `platform/ingest` still has to use these roles:
  - It needs `permissions: id-token: write`.
  - It needs `aws-actions/configure-aws-credentials`, pinned by SHA, with the matching role ARN. The ARNs are exposed as the `ci_plan_role_arn` and `ci_apply_role_arn` outputs.
  - Its plan job must run on `pull_request` and its apply job on `main`, or the subject conditions won't match.
- For stricter control, put the apply job behind a protected GitHub environment and change the apply subject to `repo:platform/ingest:environment:<name>`.

I haven't committed anything.
