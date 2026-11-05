I couldn't run `terraform fmt` here, and I made no changes.

- **`terraform fmt`:** I have no shell tool in this session, so I couldn't run it. The repository has one Terraform file, `infra/main.tf`. By inspection it already follows `fmt` style: two-space indentation and aligned `=` signs in the `ingress` block. I expect `fmt` would change nothing, but I haven't confirmed that. You can check with `terraform fmt -check -recursive`.
- **README:** `README.md` has no HCL examples and no code fences of any kind. It's 13 lines of prose describing the sandbox repo, so there was no indentation to fix. If you meant a different file or branch, tell me where the examples are.

Separately, `infra/main.tf` opens SSH (port 22) to `0.0.0.0/0` on the bastion security group. That's outside what you asked for, so I left it alone.
