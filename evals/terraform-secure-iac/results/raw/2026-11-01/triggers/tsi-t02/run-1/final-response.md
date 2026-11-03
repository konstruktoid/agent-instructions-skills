I didn't change anything, because I couldn't find the API token code you described anywhere in this workspace.

The only Terraform file here is `infra/main.tf`. All it contains is one security group:

```hcl
resource "aws_security_group" "bastion" {
  name = "bastion"
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

I also searched the whole workspace for `token`, `api_key`, and any `variable` or `output` blocks. Nothing matched, so the token variable and the output that echoes it aren't in this checkout. They may be on another branch, in a module that isn't checked out here, or in a different repo. Can you tell me where they are?

Once I can see them, the fix would be:
- Mark the token variable `sensitive = true` and remove its default.
- Delete the output that echoes it. If something downstream really needs it, mark that output `sensitive` too.
- Better still, read the token from a secrets manager (an ephemeral resource or data source) instead of passing it in as a variable, so it stays out of state. `sensitive` only hides the value in CLI output; it doesn't encrypt state.

Separately, the existing file has a real problem: `infra/main.tf:8` opens SSH (port 22) on the bastion to `0.0.0.0/0`, which is the whole internet. If you give me the CIDR ranges that should have access, I can narrow it.
