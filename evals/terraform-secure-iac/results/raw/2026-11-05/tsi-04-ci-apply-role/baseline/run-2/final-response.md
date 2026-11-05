I added `ci.tf` with the GitHub OIDC provider and two IAM roles. `terraform validate` passes, and `terraform fmt` reformatted the file. I haven't run `plan` or `apply`, so nothing has been created in AWS.

- **OIDC provider:** it trusts `token.actions.githubusercontent.com` with audience `sts.amazonaws.com`.
- **`ingest-ci-plan`:** only `pull_request` runs from `platform/ingest` can assume it. It can read the three resources in this configuration and the state file, and it can write the S3 lockfile, which plan needs.
- **`ingest-ci-apply`:** only runs on `refs/heads/main` of `platform/ingest` can assume it. It has full access to the landing bucket, the events queue and the checkpoints table, plus write access to the state object.
- **Outputs:** `ci_plan_role_arn` and `ci_apply_role_arn` are the values the workflow needs for `role-to-assume`.

I split plan and apply into two roles so a pull request, which can run modified workflow code, never gets the apply permissions. The workflow needs `permissions: id-token: write` and must use the plan role on PRs and the apply role on `main`. If the repo's apply job uses a GitHub `environment:`, the token's `sub` becomes `repo:platform/ingest:environment:<name>`, so the apply trust condition would need changing.

Before you apply this:
- **Bootstrap:** you have to apply it once from a laptop, since the roles don't exist until then.
- **Existing provider:** if the account already has a GitHub OIDC provider, which is allowed only once per account, import it instead of creating it.
- **Not scoped to your account:** the state bucket name, `ingest-terraform-state`, comes from the backend block. I couldn't check whether the state bucket is encrypted with a KMS key. If it is, both roles also need `kms:Decrypt`, and the apply role needs `kms:GenerateDataKey`.
- **Self-management:** these roles live in the same state they operate on. The apply role deliberately can't change IAM, so changes to the CI roles themselves still need a human apply.
