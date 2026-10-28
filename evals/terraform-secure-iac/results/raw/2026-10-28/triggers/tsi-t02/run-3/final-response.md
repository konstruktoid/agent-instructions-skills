I didn't change anything. The code you described isn't in this workspace.

The only Terraform file here is `infra/main.tf`, and it holds a single `aws_security_group "bastion"` resource. It has no `variable` blocks, no `output` blocks, and nothing that looks like an API token. I also checked for other `.tf`, `.tf.json` and `.tfvars` files and found none.

Even with the right file, I couldn't edit it this session: I only have tools to read and search files, not to write them or run commands. So I also couldn't run `terraform fmt`, `validate` or `tflint`.

Could you check whether the module is on another branch or path, or not committed yet? Point me to it and give me edit access, and I'll make these changes:
- **Variable:** mark the token variable `sensitive = true` and remove any default value.
- **Output:** delete the output that echoes the token. If something downstream truly needs it, keep the output but mark it `sensitive = true`.
- **State:** where the provider allows it, pass the token through a secrets manager or an ephemeral value so it isn't stored in Terraform's state file. `sensitive` only hides the value in plan and apply output; the state still holds it in plain text.
- **Checks:** run `fmt`, `validate` and `tflint` on the result.

Separately, `infra/main.tf:4-9` opens SSH (port 22) to `0.0.0.0/0`, which means anyone on the internet can reach the bastion. You probably want to limit `cidr_blocks` to known address ranges or replace the open port with SSM Session Manager. I can do that in the same pass if you'd like.
