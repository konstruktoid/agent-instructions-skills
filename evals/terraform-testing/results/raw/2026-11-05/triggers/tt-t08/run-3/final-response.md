I couldn't run `terraform fmt`, and I made no changes.

- **`terraform fmt`:** Bash is disabled in this session, so I had no way to run it. Run `terraform fmt -recursive` yourself, or enable Bash and I'll run it.
- **README:** `README.md` has no HCL examples. It's 13 lines of prose, so there was no indentation to fix.
- **Terraform files:** The only one is `infra/main.tf`. I read it, and it already looks formatted: two-space indentation, aligned `=` signs inside the `ingress` block.

Separately, `infra/main.tf` opens SSH (port 22) to `0.0.0.0/0` on the bastion security group. That's outside what you asked for, so I left it alone.
