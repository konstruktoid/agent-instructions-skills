I added `ci_iam.tf` with the GitHub OIDC provider and two IAM roles for the `platform/ingest` workflow. `terraform fmt` and `terraform validate` pass. I haven't run a plan or apply, and I haven't tested the roles against the real workflow.

**What it creates**
- **OIDC provider:** `token.actions.githubusercontent.com`, with `sts.amazonaws.com` as the audience.
- **`ingest-ci-plan`:** only a `pull_request` run from `platform/ingest` can assume it. It can read the three managed resources and the Terraform state. It can also write the state lockfile, because `plan` takes the lock.
- **`ingest-ci-apply`:** only runs on `refs/heads/main` can assume it. It can manage the landing bucket, the queue and the checkpoint table, and read and write the state and lockfile. It has no IAM permissions, so it can't change its own role.
- **Outputs:** the two role ARNs, `ci_plan_role_arn` and `ci_apply_role_arn`. Put these in the workflow's `role-to-assume`.

**What to check before applying**
- An account can only have one OIDC provider per URL. If GitHub's already exists in this account, import it instead of creating it. The import command is in a comment at the top of the file.
- I took `platform/ingest` from the README as the GitHub owner and repo. If that's wrong, edit `github_repo` in the file.
- The workflow needs `permissions: id-token: write`.
- If you use GitHub Environments for the apply job, the token's subject becomes `repo:…:environment:<name>`. The apply trust condition would then need to change.
- The roles can't be used by CI until someone applies this once from a laptop. That's the usual bootstrap step.
- The permissions were written from reading the resource types in `main.tf`. If a plan fails with access denied, add the missing read action to the plan policy.
