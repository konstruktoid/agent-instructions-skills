I found nothing to fix. The workspace has no module sources and no provider constraints.

- **Terraform files:** `infra/main.tf` is the only one. It has a single `aws_security_group.bastion` resource.
- **Modules and providers:** the file has no `module` blocks, no `source` lines, no `required_providers` or `terraform {}` block, and no version constraints. A search of all `.tf` files for `source =`, `required_providers` and `version =` returned nothing.
- **Other files:** I found no `.terraform.lock.hcl` or `.tf.json` files. The remaining files are Ansible, Docker, CI, Python and Go, with no Terraform in them.
- **Not checked:** I couldn't read the skill's `modules-supply-chain.md` reference because the read permission was denied. I made no edits and ran no Terraform commands.

The modules you describe may be on another branch or in another repository, or they may not be committed yet. If you give me the path or branch, I'll pin each module source to a commit SHA or an exact tag and add `required_providers` with pinned versions and the `hashicorp/aws` namespace. I'd also generate `.terraform.lock.hcl` for your CI platforms.

Separately, `infra/main.tf:8` opens SSH (port 22) to `0.0.0.0/0` on the bastion security group. You didn't ask about it, so I left it alone. I can restrict it to a specific CIDR if you want.
