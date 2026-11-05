I added `ci.tf` with the GitHub OIDC provider and two IAM roles for the `platform/ingest` workflow. `terraform validate` passes. I haven't run `plan` or `apply`, so nothing has been created in AWS.

- **OIDC provider:** one for `token.actions.githubusercontent.com` with audience `sts.amazonaws.com`. If the account already has one, import it rather than creating it. The import command is in a comment in the file.
- **`ingest-ci-apply`:**
  - **Trust:** only tokens whose `sub` is exactly `repo:platform/ingest:ref:refs/heads/main` can assume it, so PR runs can't.
  - **Permissions:** full access to the three resources in `main.tf` (the landing bucket, the queue and the table). It can also read and write the state object and its `.tflock` lockfile.
- **`ingest-ci-plan`:**
  - **Trust:** only `repo:platform/ingest:pull_request` tokens can assume it.
  - **Permissions:** read-only on those resources and the state, plus lockfile write. I split this into a second role because the README says `plan` runs on PRs and `apply` on `main`. A single role trusted by PRs would let any PR author apply.
- **Outputs:** `ci_apply_role_arn` and `ci_plan_role_arn`, for the workflow's `role-to-assume`.

Check these before you merge:
- **Bootstrap:** the first apply has to be done by hand, since the CI roles don't exist yet.
- **Self-management:** the roles can't change themselves, because the apply role has no IAM permissions. Changes to `ci.tf` therefore have to be applied manually. I left it that way on purpose, so CI can't grant itself more access.
- **Workflow permissions:** the workflow needs `permissions: id-token: write`.
- **Environments:** if you add a GitHub `environment` to the apply job, the `sub` becomes `repo:platform/ingest:environment:<name>`. The trust condition would need to change to match.
- **Lockfile prefix:** the S3 lockfile permission assumes the key `ingest/terraform.tfstate.tflock`, which is what `use_lockfile` produces.
