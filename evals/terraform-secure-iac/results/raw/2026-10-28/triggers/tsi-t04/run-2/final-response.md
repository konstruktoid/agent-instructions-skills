I didn't change anything. This workspace has no module sources and no provider constraints to fix.

**What's in the repository:** the only Terraform file is `infra/main.tf`, and it holds a single `aws_security_group` resource. I searched the whole workspace for `source =`, `git::`, `required_providers` and `terraform {` blocks and found none. There are no `module` blocks, no `required_providers` and no `.terraform.lock.hcl`. The Git-sourced modules you mean must live somewhere else: another branch, another directory, or another repository.

Two other limits apply:
- I only have read and search tools in this session, so I couldn't edit files or run `terraform fmt`, `validate` or `tflint` even if the modules were here.
- I couldn't open the skill's supply-chain reference file because permission to read it wasn't granted.

**What the fix would look like once I can see the files:**
- **Module sources:** pin each Git source to a full commit SHA, for example `source = "git::https://example.com/org/mod.git//path?ref=<40-char-sha>"`. A tag is only acceptable if it's protected against being moved. Use HTTPS or SSH, never put credentials in the URL, and record the version the SHA corresponds to in a comment.
- **Provider constraints:** add a `terraform { required_providers { ... } }` block. Each provider needs an explicit namespace (`hashicorp/aws`, not a bare `aws`) and an exact version or a tight constraint (`~> 5.x.y`), plus a `required_version` for Terraform itself.
- **Lock file:** run `terraform providers lock -platform=linux_amd64 -platform=darwin_arm64 …` for every platform CI uses, and commit `.terraform.lock.hcl`.
- **Checks:** run `terraform fmt -check`, `init -backend=false`, `validate` and `tflint`. `init` downloads and runs whatever the sources point at, so run it in a sandbox if the module repository isn't trusted.

**Unrelated finding:** `infra/main.tf:8` lets anyone on the internet reach SSH on port 22 (`cidr_blocks = ["0.0.0.0/0"]`). You'll probably want to restrict that to known address ranges.

Tell me where the module files are, or grant write and shell access, and I'll make the changes and run the checks.
