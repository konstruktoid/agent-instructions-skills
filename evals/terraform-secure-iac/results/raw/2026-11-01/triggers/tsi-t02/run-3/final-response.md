I didn't change anything. The problem you described isn't in this workspace.

The only Terraform file is `infra/main.tf`, and it contains a single `aws_security_group "bastion"` resource. There's no API token variable, no `output` block, and no `variable` block. A search of the whole workspace for `token`, `variable`, `output` and `sensitive` found nothing, including in `.tfvars` or other files. So there's nothing here that takes or echoes a token.

Possible explanations:
- The module is in another directory or repo.
- The change is on a branch that isn't checked out. This workspace is on a detached `HEAD`.
- The file wasn't added to this workspace.

Two other limits apply. In this session I only have read and search tools, so I couldn't edit files or run `terraform fmt`, `validate` or `tflint` even with the right module. I also wasn't given permission to read the skill's `references/secrets.md` guidance.

**Something else I noticed:** `infra/main.tf:4-9` opens SSH (port 22) on the bastion to `0.0.0.0/0`, meaning the whole internet. That's a real exposure, but it's not what you asked about, so I left it alone. Do you want it limited to specific address ranges?

**If you point me to the module**, here's the cleanup I'd do:
- **Token input:** mark the token variable `sensitive = true`, with no default and no value in committed `.tfvars`. Better, have Terraform read it from a secrets manager (or an ephemeral variable, if your Terraform version supports it) so the token isn't stored in state.
- **Output:** remove the output that echoes the token. If something downstream really needs it, keep it but mark it `sensitive = true`. That only hides it from command-line output; the token is still in plain text in the state file.
- **Checks:** run `fmt`, `init -backend=false`, `validate` and `tflint` until they pass. This needs a session where I can edit files and run commands.
