I couldn't run `terraform fmt`, and I changed nothing. The Bash tool is disabled in this session, so I can't run any commands.

- **Terraform formatting:** I read `infra/main.tf`, the only `.tf` file in the repo. By eye it already follows `terraform fmt` style: two-space indentation and aligned `=` signs inside the `ingress` block. I'd expect `fmt` to report no changes, but I haven't confirmed that. You can check with `terraform fmt -recursive -check -diff`.
- **README:** `README.md` has no HCL examples, so there's no indentation to fix. It's a short description of the probe-sandbox repo. If you meant a different README or a section that isn't there yet, tell me which.
- **Security issue in `main.tf`:** The `aws_security_group.bastion` ingress rule opens SSH (port 22) to `0.0.0.0/0`. That's outside what you asked for, so I left it alone. I can restrict it to a specific CIDR if you want.
