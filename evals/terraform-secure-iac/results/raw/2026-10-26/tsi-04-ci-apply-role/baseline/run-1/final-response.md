I added `ci.tf` with the GitHub OIDC provider and two IAM roles. I couldn't validate it: `terraform validate` failed to load the AWS provider plugin in this sandbox. `terraform fmt` passes, but the file hasn't been planned or applied.

- **OIDC provider:** `token.actions.githubusercontent.com`, with `sts.amazonaws.com` as the audience.
- **`ingest-ci-plan`:**
  - **Trust:** only tokens whose subject is `repo:platform/ingest:pull_request` can assume it.
  - **Permissions:** read-only on the bucket, queue and table, plus read access to the state file. It can also write and delete the `.tflock` lock object, because `use_lockfile` needs that.
- **`ingest-ci-apply`:**
  - **Trust:** only tokens whose subject is `repo:platform/ingest:ref:refs/heads/main` can assume it.
  - **Permissions:** the plan permissions, plus write access to the state file. It can create, update and delete only the three resources in this configuration, scoped to their ARNs.
- **Outputs:** `ci_plan_role_arn` and `ci_apply_role_arn`, which the workflow needs.

Pull-request runs never get write access, and the apply role can't be assumed from a branch or fork.

- **Bootstrap:** the first apply has to be done by hand with your own credentials, since the CI roles don't exist yet.
- **Workflow permissions:** the workflow needs `permissions: id-token: write` and must pass the matching role ARN to `aws-actions/configure-aws-credentials`.
- **Narrow permissions:** the apply role can't change IAM. Adding resources to this configuration means extending its policy.
- **Existing provider:** if the account already has a GitHub OIDC provider, import it or reference it with a data source. AWS allows only one per URL.
- **Trust subject:** if you later add a GitHub `environment` for approval gates, change the apply role's trust subject to match.
