I couldn't make either change, because the code you described isn't in this workspace.

The only Terraform file is `infra/main.tf`. It has one `aws_security_group` resource and nothing else. It has no `required_providers` block, so no `>= 4.0` provider constraint exists. It has no `module` block, so there's no Git-sourced sibling module to pin. A search of the workspace for `git::`, `.git"`, and `source =` found nothing.

The module may be on another branch, in a different directory, or not committed yet. If you tell me where it is, I'll make both changes:
- **Provider:** replace `>= 4.0` with a pessimistic constraint such as `~> 4.67`, or whichever version you've actually tested against.
- **Module source:** add `?ref=<tag-or-commit-sha>` to the Git URL. I'd need the tag or SHA you want, and a full commit SHA is the safest choice.

Separately, `infra/main.tf` opens SSH (port 22) to `0.0.0.0/0` on the bastion security group. I haven't changed it, but you may want to restrict that CIDR.
