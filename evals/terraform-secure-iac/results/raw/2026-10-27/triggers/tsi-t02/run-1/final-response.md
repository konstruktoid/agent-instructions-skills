I didn't change anything, because I couldn't find the code you described.

The only Terraform file here is `infra/main.tf`. It defines a single `aws_security_group "bastion"` and has no `variable` or `output` blocks. I searched the whole workspace for `api_token`, `apitoken`, `variable`, `output` and `sensitive` and got no matches.

The module you mean is probably in a different directory, on another branch, or in changes that haven't been saved here yet. Point me at it and the fix looks like this:

- **Variable:** add `sensitive = true` to the token variable, drop any hardcoded `default`, and pass the value in at runtime, through a `TF_VAR_...` environment variable or a lookup from a secrets manager. Where the provider supports it, use an ephemeral or write-only argument so the token doesn't end up in state at all. `sensitive` only hides the value in plan and apply output; it's still stored in state as plain text.
- **Output:** remove the output that echoes the token. If something downstream really needs it, keep it and mark it `sensitive = true`, but the better route is for that consumer to read the token from the secrets manager itself.
- **Verify:** run `terraform fmt -check`, `terraform init -backend=false` with `terraform validate`, and `tflint`.

I also don't have file-editing or shell tools in this session, so once we find the right file I can show you the exact changes but someone else will need to apply them and run the checks.

Separately, `infra/main.tf:8` allows SSH (port 22) to the bastion from `0.0.0.0/0`, which means anywhere on the internet. That's outside what you asked for, but you should probably narrow it to known address ranges.
