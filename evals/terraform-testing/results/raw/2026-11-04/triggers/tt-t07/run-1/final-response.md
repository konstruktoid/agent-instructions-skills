I couldn't make either change, because the Terraform in this workspace doesn't contain what you described. The only `.tf` file is `infra/main.tf`, and it has just one resource:

```hcl
resource "aws_security_group" "bastion" { ... }
```

It has no `required_providers` block, no `>= 4.0` constraint, and no `module` block with a Git source. I also found no other Terraform files (`.tf`, `.tf.json`, `.tfvars`) in the workspace.

The module you mean may be on another branch, in a different directory, or not committed yet. If you tell me where it is, I'll make these changes:
- **Provider:** replace `>= 4.0` with a pessimistic constraint such as `~> 4.67`, using the major version you actually run.
- **Module source:** add `?ref=<tag>` to the Git URL, ideally pinned to a release tag or a full commit SHA.

Separately, `infra/main.tf` opens SSH (port 22) to `0.0.0.0/0` on the bastion security group. You didn't ask about that, so I haven't touched it. It's probably worth restricting to known CIDR ranges.
