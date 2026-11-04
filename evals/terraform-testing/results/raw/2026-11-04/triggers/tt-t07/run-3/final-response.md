I couldn't make either change, because the code you described isn't in this repo.

- **Terraform files:** The only one is `infra/main.tf`. It has a single `aws_security_group.bastion` resource.
- **Provider pin:** There is no `required_providers` block, so no `>= 4.0` constraint exists.
- **Module source:** There is no `module` block and no Git URL.
- **Search:** A repo-wide search for `>= 4.0`, `git::` and `.git` found nothing.

The module may be on another branch, in a different directory, or not committed yet. If you point me to it, I'll make these changes:
- **Provider:** replace `>= 4.0` with a bounded constraint such as `~> 4.67`. I need to know which AWS provider version you actually run.
- **Module source:** add a `?ref=` to the Git URL. A tag like `?ref=v1.2.0` is the usual choice, and a commit SHA is stricter.

Separately, `infra/main.tf` opens SSH (port 22) to `0.0.0.0/0` on the bastion security group. I haven't changed it, but you may want to restrict that CIDR.
