I added the GitHub OIDC provider and two IAM roles (plan and apply). `terraform fmt` and `terraform validate` pass. `tflint` isn't installed here, so I didn't run it. I didn't run a plan either, because there are no AWS credentials in this environment. I haven't committed anything.

The new code is in `ci_access.tf`, `variables.tf` and `outputs.tf`.

- **OIDC provider:** `token.actions.githubusercontent.com`, audience `sts.amazonaws.com`. If the account already has this provider, import it, because AWS allows only one per URL.
- **`ingest-ci-plan` role:**
  - **Who can assume it:** only `pull_request` runs of `platform/ingest`.
  - **What it can do:** read the bucket, queue and table, and read the state object. It also has write access to the `.tflock` lock object, which is the one write plan needs.
- **`ingest-ci-apply` role:**
  - **Who can assume it:** only runs on `refs/heads/main`.
  - **What it can do:** everything the plan role can, plus the write actions on those three resources and `s3:PutObject` on the state key.
- **Permissions:** named actions only, with resource ARNs taken from the resources in `main.tf`. Sessions last one hour. No static keys are issued.
- **Variables:** the repository, branch, state bucket and state key are variables. The bucket and key defaults match the backend block, which can't take variables, so keep them in sync.
- **Outputs:** `ci_plan_role_arn` and `ci_apply_role_arn`, for use in the workflow.
- **Other files:** I added a `.gitignore` and a `.terraform.lock.hcl`. I tried to record hashes for linux and darwin on amd64 and arm64. The lock command printed an error that I only saw the tail of. Check that the lock file lists all four platforms before committing it.

Things you should know:
- **Bootstrap:** the roles are created by this same configuration, so someone has to run the first `apply` from a laptop. The roles' own IAM actions are only read on the plan role and absent from the apply role. As written, CI can't change its own roles, which I did on purpose.
- **Policy gaps:** the permission lists are written from what the AWS provider normally reads and writes. The first CI plan may fail on a missing read action, so add those one at a time instead of widening to wildcards.
- **Fork PRs:** the plan role trusts any `pull_request` run in the repository. The workflow should not run it for fork PRs.
- **Apply gate:** for a stronger gate on apply, switch the trust to a GitHub environment (`environment:<name>`) with required reviewers.
- **Workflow file:** the workflow in `platform/ingest` is not part of this change. It needs `permissions: id-token: write`, actions pinned by SHA, and `role-to-assume` set to the new role ARNs.
