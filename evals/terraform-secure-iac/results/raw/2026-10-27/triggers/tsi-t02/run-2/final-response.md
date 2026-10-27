I didn't change anything, because the API token problem you described isn't in this workspace.

- **Only one Terraform file:** `infra/main.tf` is the only Terraform file here. It holds a single `aws_security_group "bastion"` resource and nothing else: no variables, no outputs, no provider block.
- **No token anywhere:** a case-insensitive search of the whole workspace for `token`, `variable`, `output` and `secret` found nothing.

So the module you mean is probably in another repository, on another branch, or not committed yet. I also only have read and search tools in this session, so I couldn't edit files or run `terraform fmt`/`validate`/`tflint` even with the right module in front of me.

**Once I can see the module,** the fix would be:
1. Mark the token variable `sensitive = true`, give it no default, and supply it through `TF_VAR_...` or a secret manager rather than a committed `.tfvars` file.
2. Remove the output that echoes the token. If something downstream really needs it, mark that output `sensitive = true` and say so in its description. `sensitive` only hides the value in CLI output; the value is still stored in plain text in state.
3. Where the provider supports it, read the token from a secret manager or use an ephemeral resource or write-only argument, so it never reaches state at all.
4. Check git history for any committed `.tfvars` or captured plan output that contains the token. If one exists, the token should be rotated.

**Separate issue in `infra/main.tf`:** lines 4–9 open SSH (port 22) to `0.0.0.0/0`, meaning any address on the internet. You didn't ask about it, but I'd narrow it to known address ranges or replace SSH with SSM Session Manager.

Can you point me at the right path or branch, and give me edit and shell access? Then I'll make the change and run the checks.
