I didn't change anything, because the repo has nothing to fix. Its only Terraform file is `infra/main.tf`, and that file has no module blocks and no provider constraints.

- **Modules:** there are no `module` blocks anywhere, so no Git-sourced module without a ref exists here.
- **Providers:** there is no `terraform { required_providers {} }` block. The file contains one `aws_security_group.bastion` resource and nothing else.
- **Not present:** no `.terraform.lock.hcl` and no other `.tf` files.

The modules you describe are probably in another repository or branch. If you point me to it, I'll pin each module `source` to a commit SHA or protected tag, e.g. `git::https://…//path?ref=<sha>`. I'll also add `required_providers` with the right namespaces and version constraints, and commit the lock file.

If you want something done here, I could add a `required_providers` block and a lock file for the `aws` provider. Tell me which version you want.

`infra/main.tf:8` opens SSH (port 22) to `0.0.0.0/0` on the bastion security group. I'd restrict that to known CIDRs, but I haven't touched it since you didn't ask.
