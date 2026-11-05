I didn't change anything, because the module you described isn't in this workspace.

- The only Terraform file is `infra/main.tf`. It contains a single `aws_security_group.bastion` resource.
- It has no `required_providers` block, so there's no `>= 4.0` provider pin.
- It has no `module` block, so there's no Git-sourced sibling module.
- A search of the whole workspace for `git::`, `github.com` and `>= 4.0` found nothing.

The module may be on another branch or in a different directory or repository. If you point me to it, I'll make both changes:
- **Provider:** replace `>= 4.0` with a bounded constraint, such as `~> 4.67`. I'd pick the exact range from the version in your lock file.
- **Module source:** pin the Git URL to a tag with `?ref=vX.Y.Z`, or to a full commit SHA if you want it immutable.

The security group in `infra/main.tf` allows SSH (port 22) from `0.0.0.0/0`. I haven't changed it, but you may want to restrict that CIDR.
