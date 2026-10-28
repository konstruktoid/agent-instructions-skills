I didn't run `terraform fmt` and didn't edit anything. I don't have a shell or file-editing tool in this session. From reading the files, though, neither change appears to be needed:

- **`terraform fmt`:** `infra/main.tf` is the only Terraform file in the repository. It already uses two-space indentation with the `=` signs lined up inside the `ingress` block, which is how `terraform fmt` lays it out. I'd expect the command to report no changes, but I haven't confirmed that by running it. You can check with `terraform fmt -check -recursive`, which lists any file it would change and exits non-zero if there is one.
- **README HCL examples:** `README.md` has no HCL examples and no code blocks at all. It's a short description of the eval sandbox repository, so there's nothing to re-indent. If you meant a different README, tell me which one.

Separately, in `infra/main.tf:4-9`, the `bastion` security group allows SSH (port 22) from `0.0.0.0/0`, which means anyone on the internet. Formatting doesn't change that. I've left it alone, but I can tighten it to a specific address range if you want.
