I didn't change anything, because the repository has no module sources or provider constraints to fix.

The only Terraform file is `infra/main.tf`. It holds one `aws_security_group.bastion` resource and nothing else. A search for `module` blocks, `source =` and `required_providers` across `.tf`, `.hcl` and `.json` files found no matches. There is no `.terraform.lock.hcl` either. The Git-sourced modules you describe may be on another branch, in another repository, or not committed yet.

The AWS provider also has no version constraint. Nothing declares one, so Terraform will use whatever version it finds. If you'd like, I can add a `terraform` block with `required_providers` (`hashicorp/aws` pinned to a version range) and a lock file. For that I need the version you want, or I can pick a current one.

I also noticed that the bastion security group allows SSH (port 22) from `0.0.0.0/0`. That's open to the whole internet. I left it alone since you didn't ask about it, but I'd recommend restricting it to a known CIDR range, or using SSM Session Manager instead.

If the modules are elsewhere, point me at the right branch or path. For each Git module source I'd pin a ref, preferably a commit SHA or an immutable tag. I'd use an HTTPS or SSH URL with no credentials in it, and I'd pin the provider versions too.
