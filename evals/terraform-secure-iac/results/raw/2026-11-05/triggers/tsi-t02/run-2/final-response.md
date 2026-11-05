I couldn't find the API token variable or the output that echoes it, so I haven't changed anything.

The workspace has only two files, `README.md` and `infra/main.tf`. `infra/main.tf` is a single `aws_security_group.bastion` resource. It has no `variable` block, no `output` block, and nothing that mentions a token or API key. A case-insensitive search for `token`, `api_key` and `output` found no matches anywhere.

Two possibilities:
- **Another checkout or branch.** The module may live somewhere else. Tell me the path or branch and I'll work on it there.
- **Not committed yet.** The files may not be in this working tree. If you paste them, I can work from the paste.

I also read `infra/main.tf` and noticed the bastion security group allows SSH (port 22) from `0.0.0.0/0`. That is unrelated to the token, so I left it alone, but you'll probably want to restrict it.

Once I have the module, this is what I plan to do:
1. Mark the token variable `sensitive = true`.
2. Remove the output that echoes it. If something downstream needs the value, I'd mark that output `sensitive` as well.
3. Where the provider supports it, have the token come from a secret manager or an ephemeral or write-only argument, so it isn't stored in state. `sensitive` only hides the value in CLI output. It doesn't encrypt state.
4. Run `terraform fmt`, `init -backend=false`, `validate` and `tflint`.

I couldn't read the skill's `references/secrets.md` because the read was denied, so I haven't applied its guidance yet.
