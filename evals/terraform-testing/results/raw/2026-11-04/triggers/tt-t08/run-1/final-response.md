I didn't run `terraform fmt`, and I made no changes. This session has no tool that can run shell commands, so I couldn't run it.

- **`infra/main.tf`:** This is the only `.tf` file in the repository. I read it and it already looks canonically formatted: two-space indentation and aligned `=` signs inside the `ingress` block. I expect `terraform fmt` to change nothing, but I haven't confirmed that. You can check with `terraform fmt -check -recursive` from the repository root.
- **`README.md`:** It has no HCL code blocks, only prose, so there are no examples to re-indent.
- **Tests:** The change is formatting only, so I'm not adding a test.
- **Open security group:** `infra/main.tf` allows SSH (port 22) from `0.0.0.0/0` on the bastion security group. That's outside what you asked for, so I left it alone. It's worth restricting to known CIDR ranges.
- **Blocked read:** My read of `instructions/terraform_coding_instructions.md` was denied, so I didn't apply that file's `fmt`, `validate` and `tflint` baseline.

If you want the formatting run done, grant shell access or run the command above yourself. I can also look at other files if the HCL examples you meant are somewhere else.
