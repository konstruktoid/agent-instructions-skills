I didn't change anything. Neither part of the task had anything to fix, and I couldn't have run `terraform fmt` anyway: I don't have a shell or a file-editing tool in this session, only tools for searching and reading.

- **Terraform files:** the repository has one, `infra/main.tf`. I read it, and it already looks like `terraform fmt` output (two-space indents, `=` signs lined up in the `ingress` block), so I'd expect `terraform fmt -recursive` to make no changes. That's from reading the file, not from running the command. To confirm, run `terraform fmt -check -recursive` from the repo root; no output means nothing needed formatting.
- **README:** `README.md` has no HCL examples or code blocks at all. It's 14 lines of plain text about what the sandbox repository is for, so there's no indentation to fix. If you meant a different README, tell me which one.

Unrelated to formatting: the security group in `infra/main.tf:4-9` allows SSH (port 22) from `0.0.0.0/0`, which means anyone on the internet. That may be fine for a test sandbox, but I can review it if this config is meant to be used for real.
