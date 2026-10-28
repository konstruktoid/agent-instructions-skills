I added `ci_access.tf`, which creates the GitHub OIDC provider and two IAM roles for the platform/ingest workflow. I couldn't validate it: `terraform fmt` and `terraform init` failed in this sandbox with an error about the binary. The file is unformatted and unvalidated, so run `terraform fmt` and `terraform validate` before using it.

- **OIDC provider:** it uses `token.actions.githubusercontent.com` with the audience `sts.amazonaws.com`.
- **Plan role, `ingest-terraform-plan`:**
  - **Assumption:** only the `pull_request` token from `repo:platform/ingest` can assume it.
  - **Permissions:** it can read the managed resources and the state. It can also write the S3 lockfile, because `use_lockfile` needs that even for a plan.
- **Apply role, `ingest-terraform-apply`:**
  - **Assumption:** only `repo:platform/ingest:ref:refs/heads/main` can assume it.
  - **Permissions:** it can create, change and delete the bucket, queue and table, and write the state. Those permissions are limited to their ARNs. It has no IAM permissions and no access to object data.
- **Outputs:** `ci_plan_role_arn` and `ci_apply_role_arn` give you the role ARNs for the workflow.

**Workflow side:** each job needs `permissions: id-token: write` and must pass its role ARN to `aws-actions/configure-aws-credentials`.

**Bootstrap:** the roles live in this same configuration. Someone has to apply this once from a laptop before CI can take over.

**Gaps to check:**
- The action lists are my best guess at what the AWS provider calls. Run a plan and an apply through CI and add any permission denials it reports.
- If you later want approval gates on apply, switch the apply trust to a GitHub environment subject (`repo:platform/ingest:environment:<name>`).
