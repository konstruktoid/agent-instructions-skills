I didn't change anything. This workspace has no module sources or provider constraints to fix.

**What's here:** the only Terraform file is `infra/main.tf`. It holds one resource, `aws_security_group.bastion`, and nothing else:
- There are no `module` blocks, so no Git `source` exists to pin.
- There is no `terraform { required_providers { ... } }` block and no `required_version`.
- There is no `.terraform.lock.hcl`.

A search of the whole repository for `source`, `module`, `git::` and `required_providers` matched only that resource line.

**I also can't edit files in this session.** I only have read and search tools here, with no edit or shell access. So I couldn't write a fix or run `terraform fmt`, `terraform validate` or `tflint`. I also wasn't allowed to read the skill's supply-chain guidance file.

**Something else I noticed:** `infra/main.tf:4-9` lets anyone on the internet reach SSH (port 22, from `0.0.0.0/0`) on the bastion host. If that's not intended, the allowed addresses should be limited to known ranges.

**What I'd need to go further:**
1. Point me at the module code if it's somewhere else, like another branch, directory or repository.
2. If you want it, I can add a provider block from scratch, though it wouldn't fix any existing problem. It would pin the AWS provider as `hashicorp/aws` with a version constraint, set a `required_version`, and commit a lock file covering the platforms CI uses. I'd need the AWS provider and Terraform versions you run, and permission to edit files and run commands.

For any Git module you add later, pin the `source` to a full commit SHA (`git::https://...?ref=<40-char sha>`) rather than a branch, or to a tag that can't be moved.
