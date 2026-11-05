I added the GitHub OIDC provider and two CI roles. `terraform fmt -check` and `terraform validate` pass. The multi-platform lock file is not done, I didn't run `tflint`, and I haven't planned or applied anything. Nothing is committed.

**What was added**
- `ci_iam.tf` has the OIDC provider and the roles.
  - **Provider:** `token.actions.githubusercontent.com`, with audience `sts.amazonaws.com`.
  - **`ingest-ci-plan`:**
    - **Who can assume it:** only `repo:platform/ingest:pull_request`.
    - **Access:** read-only on the bucket, queue and table, plus read of the state object. It can also write the state lock object, because the backend uses `use_lockfile`.
  - **`ingest-ci-apply`:**
    - **Who can assume it:** only `repo:platform/ingest:ref:refs/heads/main`.
    - **Access:** the same read access, plus named create/modify/delete actions on those three resources and write to the state object.
- `variables.tf` has the repository, apply branch, state bucket and state key as variables. The defaults come from the README and `versions.tf`.
- `outputs.tf` exposes both role ARNs, which the workflow uses as `role-to-assume`.
- `.gitignore` is new. It covers `.terraform/`, state files and plan files.

**Security choices**
- The trust conditions are exact `StringEquals` matches with no wildcards. Plan and apply have separate roles, and apply can only be assumed from the protected branch. Sessions last at most one hour and there are no static keys.
- Every permission is a named action on a specific ARN, so there are no `*` actions or resources.
- I did not set `s3:PutObject` or `DeleteObject` on the state file for the plan role.

**Not done**
- `terraform providers lock` failed for other platforms: it couldn't write to a temp directory in this environment. `.terraform.lock.hcl` currently records only the local platform, so you'll need to run `terraform providers lock -platform=…` for each platform CI uses before committing it.
- `tflint` isn't installed here, and the repo has no scanner configured.

**Things to check before applying**
- AWS allows only one OIDC provider per issuer URL. If the account already has the GitHub one, import it with `terraform import aws_iam_openid_connect_provider.github <arn>` instead of creating it.
- The roles manage the resources in `main.tf` and the state file, so the first apply has to run from the laptop. The roles also don't cover creating or changing IAM, so changes to them stay a manual step.
- If the workflow uses a GitHub `environment:` for approvals, the token subject changes to `repo:…:environment:<name>`. The apply trust condition would need updating to match.
