I didn't change anything, because the module you described isn't in this workspace.

The only Terraform file is `infra/main.tf`. It holds a single `aws_security_group.bastion` resource and nothing else. It has no `required_providers` block, no `>= 4.0` provider constraint, and no `module` block with a Git source. I also searched all `*.tf` files for those patterns and found no matches.

Separately, that security group allows SSH (port 22) from `0.0.0.0/0`. That's worth restricting, but it's outside what you asked for, so I left it alone.

Can you tell me where the module is? It may be on another branch, in a different directory, or not yet committed. If you'd like me to add the constraints to this file, I need two things from you:
- **Provider:** the provider name and the version range you want, such as `~> 5.0`.
- **Sibling module:** its Git URL and the tag or commit SHA to pin it to.
