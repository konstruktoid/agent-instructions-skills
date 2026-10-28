I didn't run `terraform fmt` or edit any files, because this session has no shell or file-editing tools. I read the files by hand instead, and neither one needs changing.

- **`infra/main.tf`** (the only Terraform file in the repository) already looks like `terraform fmt` output: two-space indentation, aligned `=` signs in the `ingress` block, and a trailing newline. I'd expect `terraform fmt -recursive` to make no changes, but I haven't run it to confirm.
- **`README.md`** has no HCL examples or code blocks at all. It's 14 lines of prose about the repository's purpose, so there's no indentation to fix.

You can confirm the first point with `terraform fmt -check -recursive -diff`. If the HCL examples you meant are in a different README, tell me where and I'll look.

Separately, `infra/main.tf:8` opens SSH (port 22) to `0.0.0.0/0`, meaning anyone on the internet. Formatting won't flag that. If this is real infrastructure and not just sample material, you'd want to limit that range to known addresses.
