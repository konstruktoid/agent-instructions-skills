I added `ci.tf` with the GitHub OIDC provider and two IAM roles for the `platform/ingest` workflow. `terraform fmt` and `terraform validate` both pass. I haven't run a plan or apply, so the roles haven't been tried against AWS.

- **OIDC provider:** `token.actions.githubusercontent.com` with audience `sts.amazonaws.com`. An account can only have one provider for that URL. If this account already has one, import it with `terraform import aws_iam_openid_connect_provider.github <arn>` instead of creating it.
- **`ingest-ci-plan` role:** for the pull-request `plan` runs. Only tokens whose subject is `repo:platform/ingest:pull_request` can assume it. It has read-only access to the three managed resources and to the state file. It can also write the `.tflock` lock object, because `use_lockfile = true` needs that even for a plan.
- **`ingest-ci-apply` role:** for the `apply` run on merge. Only tokens whose subject is `repo:platform/ingest:ref:refs/heads/main` can assume it. It has full actions on the landing bucket, the queue and the table, and can write the state file. It has no IAM permissions, so it can't widen its own access.
- **Outputs:** `ci_plan_role_arn` and `ci_apply_role_arn`.

I used two roles because the README splits the work that way. A pull request, which anyone can open, never gets write access.

- **Bootstrap:** apply this once from a laptop, since CI can't create its own role. Then give the workflow `permissions: id-token: write` and pass it the role ARNs.
- **Hardcoded names:** the resource names and the state bucket are written out in `ci.tf`, not read from the resources in `main.tf`. If you rename a resource, update the policy too.
- **Environments:** if the workflow uses a GitHub `environment:` for apply, the token subject becomes `repo:platform/ingest:environment:<name>`. The apply role's trust condition would need to change to match.
