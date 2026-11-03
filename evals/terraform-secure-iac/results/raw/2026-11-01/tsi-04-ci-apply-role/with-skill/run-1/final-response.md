I added the GitHub OIDC provider and two CI roles in a new `bootstrap/` directory. The lock file only covers this machine's platform, so multi-platform checksums still need doing. Nothing is committed.

**Checks**
- `terraform fmt -check` is clean.
- `terraform validate` passes after `init -backend=false`.
- `checkov` passed 89 checks with 0 failures.
- `tflint` isn't installed here, so I didn't run it.
- I didn't run a backend-enabled `plan` because I had no AWS credentials.
- `terraform providers lock` for the other platforms failed with "disk quota exceeded" in the temp directory. `bootstrap/.terraform.lock.hcl` therefore holds only the checksums from `init`. Before CI relies on it, run `terraform providers lock -platform=linux_amd64 -platform=linux_arm64 -platform=darwin_arm64 -platform=darwin_amd64` in `bootstrap/` on a machine with space.

**What's in `bootstrap/`**
- **Separate root:** it has its own state key, `ingest/bootstrap/terraform.tfstate`. The CI roles hold no IAM permissions, so the apply role can't rewrite its own trust or policy. Someone with AWS admin access applies `bootstrap/` by hand, once.
- **OIDC provider:** it is created for `token.actions.githubusercontent.com` with audience `sts.amazonaws.com`.
- **`ingest-ci-plan` role:** only `pull_request` runs of `platform/ingest` can assume it. It can read the three managed resources and the state object. It can also write the state lock file.
- **`ingest-ci-apply` role:** only runs on `refs/heads/main` of `platform/ingest` can assume it. It can create, update and delete the bucket, queue and table, and write the state object. The repository and branch are variables, and the repository is checked against a pattern with no wildcards.
- **Permissions:** actions are named and each is limited to a specific resource ARN, with no wildcards. Sessions last an hour by default.
- **Other files:** I added a `.gitignore` for state, plan and `.terraform/` files, and a README section on how to wire up the workflow.

**Things to check**
- The permission lists are my best guess at what the AWS provider calls. If a plan or apply fails with `AccessDenied`, add the missing named action to `bootstrap/main.tf`.
- The workflow itself isn't in this repo. It needs `permissions: id-token: write` and the two role ARNs from the outputs as `role-to-assume`.
- The state bucket has to exist already, as it does today.
- The `pull_request` trust is open to any PR run in the repository. If forks can open PRs there, check that the workflow doesn't expose the plan role to them.
