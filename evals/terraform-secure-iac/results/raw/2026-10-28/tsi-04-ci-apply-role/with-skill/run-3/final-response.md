I added the GitHub OIDC provider and two CI roles in a new `ci-identity/` root. `terraform fmt` is clean, but `terraform validate` and `tflint` did not run, so the configuration is unvalidated.

**What's in `ci-identity/`**
- **OIDC provider:** `token.actions.githubusercontent.com`, with audience `sts.amazonaws.com`.
- **`ingest-ci-plan`:** assumable only by `pull_request` runs of `platform/ingest`. It has read access to the bucket, queue and table, and to the state object. It also has the state lock object, which `use_lockfile` needs even for a plan, and no write access to the state itself.
- **`ingest-ci-apply`:** assumable only from `refs/heads/main`. It has the same read access plus create, update and delete on those three resources, and write on the state object.
- **Trust policies and permissions:** the trust policies match `aud` and an exact `sub` with no wildcards. Permissions name the resources and the account and region come from data sources. Sessions last 1 hour by default. There is no static key anywhere.
- **Other files:** the root has its own state key, `ingest/ci-identity/terraform.tfstate`. It also has a README, a `.terraform.lock.hcl` covering linux_amd64 and darwin_arm64, and a top-level `.gitignore`.

**Why a separate root:** if the roles lived in the main configuration, the apply role would need IAM write access to manage itself. Anyone who could change a merged workflow could then widen their own permissions. An administrator applies this root once, by hand. The cost is one extra manual bootstrap step.

**Verification**
- `terraform fmt -check` passes.
- `terraform init -backend=false` succeeded, but `terraform validate` failed. The AWS provider binary would not start in this sandbox (plugin handshake failure). My first install attempt also hit a disk quota error. I did not retry further. I deleted the temporary provider install.
- `tflint` and the configuration scanners (`trivy`, `tfsec`, `checkov`) are not installed here, and the repo configures none.
- I ran no plan, since there are no AWS credentials. Please run `validate` and `tflint` in CI or locally before applying.

**Before you apply**
- The workflow needs `id-token: write`. Use `aws-actions/configure-aws-credentials` pinned by commit SHA, with the plan role on pull requests and the apply role on pushes to `main`.
- If the account already has a GitHub OIDC provider, import it first. AWS allows only one per issuer URL. The README gives the command.
- The IAM actions are my best estimate for these three resource types. Expect to add a few after the first plan returns `AccessDenied`.
- I assumed the `platform/ingest` repo means owner `platform`, name `ingest`. This is the `github_repository` variable, and I haven't checked it against the real repo.
- For an approval gate, put the apply job in a GitHub environment with required reviewers. Then change the apply role's `sub` to the environment form.

I haven't committed anything.
