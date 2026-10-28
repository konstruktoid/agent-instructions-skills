I didn't change anything, because the code you described isn't in this workspace. The only Terraform file is `infra/main.tf`, and it has no API token variable, no `variable` blocks and no `output` blocks. It defines one security group.

**A separate problem in that file:** `infra/main.tf:8` opens SSH (port 22) to `0.0.0.0/0`, so the whole internet can reach the bastion. You may want to limit it to a known admin CIDR range, use a variable for that, or move to SSM Session Manager and drop the rule.

**For the token code, once I can see it, the fix would be:**
- Mark the token variable `sensitive = true` and leave it with no default value.
- Delete the output that echoes it. If something downstream really needs the value, mark that output `sensitive` too.
- If possible, have the module read the token from a secret manager (data source or ephemeral resource) instead of taking it as an input. That keeps it out of `.tfvars` and, where the provider allows, out of state. `sensitive` only hides the value in CLI output; it still sits in state in plaintext.
- Check that no `.tfvars` file or captured plan output with the real token has been committed.

**To go further, I need:**
- **The right code:** the module may be on another branch, in another directory, or not committed yet. Tell me where it is.
- **Tools:** this session only lets me search and read files. I can't edit files or run `terraform fmt`, `validate` or `tflint`, so I'll need edit and shell access to make and check the change.
- **A permission:** I was blocked from reading the skill's `references/secrets.md` guidance, so the advice above comes from general Terraform practice. If you grant read access to it, I'll check it before editing.
