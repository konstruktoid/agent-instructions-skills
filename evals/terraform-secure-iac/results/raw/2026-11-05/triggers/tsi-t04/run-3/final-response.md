I made no changes, because the workspace has no module sources or provider constraints to fix.

- **Terraform files:** `infra/main.tf` is the only one. It has a single `aws_security_group` resource and no `module` blocks. It has no `terraform { required_providers }` block and no `version` constraints.
- **Git sources:** A search of the whole workspace for `git::`, `git@`, `.git` and `module "` found nothing. That covers the CI files, Dockerfile and scripts too.

The modules you describe may be on another branch or in another directory or repository. If you point me to them, I'll pin each Git `source` to a commit SHA or a protected tag with `?ref=`. I'll also add `required_providers` with the right namespaces and version constraints, and make sure `.terraform.lock.hcl` is committed.

I could add a `required_providers` block for `aws` to `infra/main.tf`. That would be a new constraint rather than a fix, and I'd need to know which version range you want.

**Open SSH rule:** The security group in `infra/main.tf:8` allows SSH (port 22) from `0.0.0.0/0`. You didn't ask about it, so I left it alone. I can restrict it to a specific CIDR if you want.
