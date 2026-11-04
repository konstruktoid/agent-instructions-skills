I haven't changed anything, because `infra/main.tf` has neither of the things you described. It's the only `.tf` file in the workspace, and it contains just this:

```hcl
resource "aws_security_group" "bastion" {
  name = "bastion"
  ingress { from_port = 22, to_port = 22, protocol = "tcp", cidr_blocks = ["0.0.0.0/0"] }
}
```

- **Provider pin:** there is no `terraform { required_providers { ... } }` block, so no `>= 4.0` constraint exists.
- **Module source:** there is no `module` block, so there is no Git URL to add a ref to.

The module you mean may be on another branch or in a different directory or repo. If you point me to it, I'll tighten both.

If you want me to add the constraints here instead, I need two things from you. Which AWS provider range do you want, for example `~> 5.0`? Which sibling module and ref (tag or commit SHA) should I pin?

Separately, this security group allows SSH from `0.0.0.0/0`. That's worth restricting to known CIDRs, and I can do that too if you'd like.
