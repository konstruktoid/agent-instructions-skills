I didn't change anything. The module you described isn't in this workspace.

- **The only Terraform file is `infra/main.tf`.** It holds one resource, `aws_security_group.bastion`. It has no `variable` blocks, no `output` blocks and no API token.
- **Nothing else in the repo matches.** A case-insensitive search of the whole workspace for `token`, `variable` and `output` returned nothing. There are no other `.tf` or `.tfvars` files.

The module may be on another branch or in another repo. This session also only gives me read and search tools, so I can't edit files even once we find it.

If you point me to the right module, this is the fix:
1. Mark the token variable `sensitive = true`, with no default, and supply it from the environment (`TF_VAR_...`) or a secrets manager. It shouldn't be in a committed `.tfvars` file.
2. Delete the output that echoes the token. Nothing downstream should need to read the token back from Terraform. If something really does, mark that output `sensitive = true` too.
3. Remember that `sensitive` only hides the value in plan and apply output. The token is still stored in plain text in state. Where the provider supports it, a write-only argument or an ephemeral resource keeps it out of state, and the state backend needs encryption and access control either way.
4. Check that the token was never committed or printed in old CI logs. If it was, it needs to be rotated.

Unrelated to the token: `infra/main.tf:8` opens SSH (port 22) to `0.0.0.0/0`, so anyone on the internet can reach the bastion host. That's worth restricting to known address ranges.
