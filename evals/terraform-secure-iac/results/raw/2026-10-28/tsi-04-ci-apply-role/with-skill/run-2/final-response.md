I added `ci_access.tf`, which creates the GitHub OIDC provider and two IAM roles for the workflow. `terraform fmt -check` is clean. I did not run `terraform init`, `terraform validate` or `tflint`, so the HCL is not validated. `init` downloads and runs provider plugins, and I had no sandbox for that here. `tflint` isn't installed, and no config scanner is configured in the repo. I haven't applied anything.

**What it creates**
- **OIDC provider:** `aws_iam_openid_connect_provider.github`, with audience `sts.amazonaws.com`. There are no static keys anywhere.
- **`ingest-ci-plan`:** the role the pull-request plan job assumes. Only tokens whose subject is `repo:platform/ingest:pull_request` can assume it. It is read-only on the three managed resources and read-only on the state object. It can also write the `.tflock` lock object, because `use_lockfile` makes `plan` create and delete it.
- **`ingest-ci-apply`:** the role the apply job assumes on merges to main. Only tokens whose subject is `repo:platform/ingest:ref:refs/heads/main` can assume it. It has the plan role's read access plus create, update and delete on the bucket, queue and table, and write on the state object. Actions are named and scoped to the ARNs of the managed resources. It has no IAM permissions, so it can't widen its own access.
- **Outputs:** `ci_plan_role_arn` and `ci_apply_role_arn`, for the workflow's `role-to-assume`.

**Choices to check**
- **Two roles:** you asked for one role, but I split plan and apply so a pull request never holds write credentials.
- **Repo and ref variables:** the repo and ref are the variables `github_repository` and `github_apply_ref`, defaulting to `platform/ingest` and `refs/heads/main`.
- **Environment instead of ref:** if the apply job uses a protected GitHub Environment, change the subject to `repo:platform/ingest:environment:<name>`.
- **Permission list:** the permission lists come from what the AWS provider normally reads and writes for these resource types. The first `plan` or `apply` may need an action added. Add only what the failure names.
- **Bootstrap:** the first apply has to run from a laptop with IAM rights, since the roles don't exist yet. The workflow can take over after that.
- **State bucket name:** the state bucket ARN in `locals` is hardcoded to match the backend block. Backend blocks can't take variables, so keep the two in sync.
- **Workflow side:** the workflow file isn't in this repo. It needs `permissions: id-token: write`, `aws-actions/configure-aws-credentials` pinned by commit SHA, and `apply` restricted to main.
