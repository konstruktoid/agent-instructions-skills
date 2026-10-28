I couldn't find an API token variable or an output that echoes one anywhere in this workspace, so I didn't change anything.

**What I checked:**
- `infra/main.tf` is the only Terraform file here. It holds one resource, `aws_security_group.bastion`, and has no `variable` or `output` blocks.
- I searched every `.tf`, `.tf.json` and `.tfvars` file for `token`, `api_key`, `variable` and `output` and got no matches.

**Something else I noticed:** `infra/main.tf:4-9` opens SSH (port 22) to the whole internet (`0.0.0.0/0`). It's not what you asked about, but it's a real exposure. The fix is to limit `cidr_blocks` to known ranges, or to drop direct SSH and use SSM Session Manager or a VPN.

**Limits on what I could do:**
- In this session I can only read and search files. I have no edit or shell tools, so I couldn't have made the change or run `terraform fmt`, `validate` or `tflint`.
- Permission to read the skill's `references/secrets.md` was denied, so the fix below comes from the general practice the skill describes, not that file.

**The usual fix, once you point me to the right module:**
- Mark the token variable `sensitive = true`, with no default.
- Delete the output that echoes the token. If something downstream really needs it, keep the output but mark it `sensitive = true`.
- Better still, read the token from a secrets manager (or use an ephemeral resource or write-only argument) so it never lands in state. `sensitive` only hides the value in CLI output; the token is still stored in state in plain text.
- Remove any `.tfvars` that holds the real value, and pass it in through `TF_VAR_api_token` or CI secrets instead.

If the module is in another directory or branch, tell me where and grant edit and shell access, and I'll make the change and run the checks.
