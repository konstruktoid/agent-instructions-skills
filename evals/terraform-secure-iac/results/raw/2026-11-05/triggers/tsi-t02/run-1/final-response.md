I couldn't find the token variable or the output, so I haven't changed anything.

The workspace has one Terraform file, `infra/main.tf`, plus a `README.md`. `main.tf` contains only an `aws_security_group.bastion` resource. A search for "token", "variable" and "output" found nothing anywhere in the workspace.

Two likely explanations:
- The module is in a different directory or repository, and this workspace isn't the right checkout.
- The changes are on another branch, or haven't been committed yet.

Tell me where the module is and I'll make the change there. For an API token, I'd do this:
- Mark the variable `sensitive = true`.
- Remove the output, or mark it `sensitive` if something consumes it. Marking it `sensitive` only hides it in CLI output. The value still ends up in state.
- Preferably, stop passing the token as a plain variable. Read it from a secrets manager at apply time, or use an ephemeral resource or write-only argument if your Terraform and provider versions support them. That keeps the token out of state.

I'd then run `terraform fmt`, `terraform validate` and `tflint` through the repo's own tooling.

Separately, `main.tf:8` opens SSH (port 22) on the bastion security group to `0.0.0.0/0`. You didn't ask me to change that, so I've left it alone. It's worth restricting to known CIDRs.
