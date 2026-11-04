I couldn't find a `test/` directory in this repo, so I have no unfamiliar Terraform tests to point you to. There's also no module here for your new input to belong to.

**What's in the repo:**
- **Terraform:** `infra/main.tf` is the only file. It's a single `aws_security_group.bastion` resource with no `variable` blocks, so it isn't a module yet.
- **Test files:** there are no `.tftest.hcl` files, no Terratest (the only Go file is `cmd/parser.go`, which has no Terraform tests), and no plan-and-policy scripts.
- **CI:** `.github/workflows/deploy.yml` doesn't run any Terraform commands.
- **README:** it says this is a mixed sandbox repo used only for trigger evals. It's a stand-in rather than a real project.

**Possible explanations:**
- You may be in a different checkout or branch from the one with those tests. If so, point me at the right directory and I'll look there.
- The tests may be untracked or gitignored. The git status only shows an untracked parent directory.
- They may be Python tests for a different part of the repo. The README mentions a Python package with tests, but I haven't looked at it.

**Where a test would go:** the skill says to follow the repo's existing convention. There isn't one for Terraform here, so there's nothing to match. For a module with no tests, the default is native `terraform test`, with a `tests/` directory next to the module (for example `infra/tests/<name>.tftest.hcl`). The conditions are:
- **Version:** both `required_version` and the Terraform version CI runs must be 1.6 or later. If you use `mock_provider`, they must be 1.7 or later. `infra/main.tf` doesn't pin a version.
- **Run blocks:** use `command = plan` so nothing gets created.
- **Coverage:** assert the new input's effect on the resource. If it has a `validation` block, include one run that rejects a bad value (with `expect_failures`) and one that accepts a good value.

If you share the real repo's `test/` contents, or the new input's definition, I can say exactly where its test goes and write it.
