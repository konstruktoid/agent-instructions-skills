I added `ci.tf`, which defines the GitHub OIDC provider and two IAM roles for the `platform/ingest` workflow. `terraform fmt` and `terraform validate` pass. I haven't run a plan or apply, so none of it has been tested against AWS or a real workflow run.

**What it creates**
- **OIDC provider:** `token.actions.githubusercontent.com`, with the audience set to `sts.amazonaws.com`. It sets no thumbprint, because AWS validates GitHub's certificate itself.
- **`ingest-ci-apply` role:**
  - **Who can assume it:** only the `main` branch of `platform/ingest` (`repo:platform/ingest:ref:refs/heads/main`). Pull requests, forks and other branches cannot.
  - **What it can do:** manage the landing bucket, the events queue and the checkpoints table, plus read and write the state file and its lockfile.
- **`ingest-ci-plan` role:**
  - **Who can assume it:** pull-request runs only (`repo:platform/ingest:pull_request`).
  - **What it can do:** read the three managed resources and read the state. It can write only the lockfile (`ingest/terraform.tfstate.tflock`), so a PR plan cannot change state or infrastructure.
- **Outputs:** `ci_apply_role_arn` and `ci_plan_role_arn`, to put in the workflow.

I split plan and apply so that a pull request, including one that edits the workflow file, never gets write access.

**Things to check**
- **Bootstrap order:** the first apply has to run from the laptop, since the roles don't exist yet.
- **Workflow permissions:** the workflow needs `permissions: id-token: write`.
- **Existing provider:** if the account already has a GitHub OIDC provider, apply will fail because AWS allows one per URL. Import it or reference it with a data source instead.
- **New resources:** if you add resources to this configuration, extend the apply role's permissions to cover them.
- **Branch protection:** the apply role trusts anything that lands on `main`, so make sure branch protection on `main` is in place.
