I didn't change anything. There was nothing to fix, and I couldn't have run the formatter anyway.

- **No HCL examples in the README.** `README.md` is 14 lines of prose describing this as a sandbox repository for trigger evals. It has no code blocks of any kind, so there's no indentation to fix. You might mean a README somewhere else, perhaps in the parent `agent-instructions-skills` repo.
- **`terraform fmt` wasn't run.** I can only read and search files in this session. I have no shell and no way to edit files. The only Terraform file is `infra/main.tf`, and by inspection it already looks like `terraform fmt` output: 2-space indents and lined-up `=` signs in the `ingress` block. I expect `terraform fmt -recursive -check` would report nothing, but I haven't run it to confirm.

Separately, `infra/main.tf:8` allows SSH from anywhere (`cidr_blocks = ["0.0.0.0/0"]`) on the bastion security group. Formatting won't catch that. I've left it alone because it's outside what you asked, and since this sandbox is meant to look realistic, it may be deliberate.

If you point me to the README you meant, or give me shell and edit access, I'll run `terraform fmt -recursive` and fix the indentation in its HCL blocks.
