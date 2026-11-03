I didn't change anything, because I couldn't find what you described. This workspace has no API token variable and no output that echoes one.

- **Only Terraform file:** `infra/main.tf` holds a single `aws_security_group "bastion"` resource, with no `variable` or `output` blocks.
- **Repo-wide search:** a case-insensitive search for `token`, `variable` and `output` across the whole workspace found nothing.

There may be a different directory or branch you meant (the repo's current state is a detached HEAD), or the module hasn't been committed yet. If you point me to it, the cleanup would be:

1. Mark the token variable `sensitive = true` and remove any default value.
2. Delete the output that echoes the token. If something downstream really needs it, mark that output `sensitive` too.
3. Where the provider supports it, fetch the token from a secrets manager or pass it through an ephemeral or write-only argument so it stays out of state. `sensitive` only hides a value in CLI output; it still gets saved in state as plain text.
4. Run `terraform fmt`, `validate` and `tflint` on the result.

While looking I noticed that `infra/main.tf:4-9` lets SSH (port 22) in from anywhere (`0.0.0.0/0`). You didn't ask about this, but it should probably be limited to known address ranges.

I also couldn't read the skill's secrets reference file because the read permission was denied. I'll need it once there's real code to change.
