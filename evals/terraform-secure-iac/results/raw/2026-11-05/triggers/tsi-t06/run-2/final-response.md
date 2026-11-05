I couldn't run `terraform fmt` because the Bash tool is disabled in this session. I also made no edits, because I found nothing that needed fixing.

- **`infra/main.tf`:** This is the only Terraform file. By inspection it already follows `terraform fmt` style: two-space indentation and aligned `=` signs inside the `ingress` block.
- **`README.md`:** It has no HCL examples or code blocks, so there was no indentation to fix.

If you have a different README in mind, tell me where it is. Once Bash is available, run `terraform fmt -recursive -check` to confirm the formatting.

`infra/main.tf` opens SSH (port 22) to `0.0.0.0/0` on the bastion security group. I left it alone because you only asked for formatting. I can restrict it to a specific CIDR if you'd like.
