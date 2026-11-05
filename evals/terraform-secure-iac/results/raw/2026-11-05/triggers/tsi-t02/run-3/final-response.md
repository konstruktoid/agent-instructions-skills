I couldn't find the module you described, so I haven't changed anything.

The workspace has only one Terraform file, `infra/main.tf`. It defines an `aws_security_group.bastion` resource and has no variables, outputs or API token. A search of the whole workspace for "token", "variable" and "output" returned nothing.

Two things might explain it. The module may be on another branch or in another directory. Or it may not have been committed to this checkout yet. If you point me to the right path or branch, I'll make the fix.

I also couldn't read the skill's `references/secrets.md`. That read needs a permission I haven't been granted.

Once I find the module, I'd make these changes:
- Mark the token variable `sensitive = true`.
- Remove the output that echoes the token. If something downstream needs it, I'd mark that output `sensitive` or have the consumer read it from a secrets manager.
- Check whether the token can come from a secrets manager or an ephemeral or write-only argument. That would keep it out of state, because `sensitive` only hides the value in CLI output.

While looking, I noticed that `infra/main.tf:8` opens SSH on the bastion to `0.0.0.0/0`. That is a separate problem, and I haven't touched it. I can tighten it if you want.
