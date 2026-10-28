I added `ci.tf` with the GitHub OIDC provider and two IAM roles for the `platform/ingest` workflow. `terraform fmt` passes, but `terraform validate` didn't run: the AWS provider plugin failed to start in this sandbox. Nothing has been planned or applied, so please run `terraform validate` and a plan before merging.

**What's in it**
- **OIDC provider:** `token.actions.githubusercontent.com`, with audience `sts.amazonaws.com`. An account can only have one provider per issuer URL. If this account already has one, import it instead of creating a second.
- **`ingest-ci-plan`:** only the workflow's pull-request jobs can assume it (`repo:platform/ingest:pull_request`). It has read-only access to the bucket, queue and table, and read access to state. It can also write the `.tflock` lock object, because plan takes the lock when `use_lockfile` is on.
- **`ingest-ci-apply`:** only the workflow running on `refs/heads/main` can assume it. It can create, change and delete the three resources and write state. Its S3 rights are on the bucket itself, with no object read or write on the landing data.
- **Scoping:** both roles are limited to the exact ARNs for the three resources and the state key. There is no admin or wildcard access beyond a few read calls.
- **Outputs:** `ci_plan_role_arn` and `ci_apply_role_arn` give you the ARNs for the workflow's `role-to-assume`.

**To check before relying on it**
- The workflow needs `permissions: id-token: write`.
- If the workflow's `apply` job uses a GitHub `environment:`, the token's subject becomes `repo:platform/ingest:environment:<name>`. The trust condition on the apply role would then need to match that instead.
- The first apply of this change still has to run from a laptop, since the roles don't exist yet.
- This configuration is staging-only (the resource names end in `-staging`). Nothing separates a future prod config from these roles.
