I couldn't run `terraform fmt`, and I made no changes. I have no shell or file-editing tool in this session, only read and search tools. The skill's tooling-baseline file also failed to load because the read was denied.

- **`infra/main.tf`:** this is the only Terraform file in the repo. Reading it, the indentation already looks `terraform fmt`-clean (2-space nesting, aligned `=` in the `ingress` block). I haven't confirmed that with the tool.
- **`README.md`:** it has no HCL examples or code blocks, so there is no indentation to fix. It only describes the sandbox repo.
- **Tests:** the repo has no `.tftest.hcl` files, and a formatting-only change doesn't need one.

To confirm, run `terraform fmt -check -recursive -diff` from the repo root. If you give me shell access, I'll run it and apply any changes.

Separately, `infra/main.tf` opens SSH (port 22) to `0.0.0.0/0` on the bastion security group. I left it alone since you didn't ask about it, but you may want to restrict it.
