I couldn't apply the change because the Write tool is disabled in this session. I haven't edited anything, and I haven't run `terraform validate` or `plan`. The module is a single file, `infra/main.tf`, and it only has the `bastion` security group:

```hcl
ingress {
  from_port   = 22
  to_port     = 22
  protocol    = "tcp"
  cidr_blocks = ["0.0.0.0/0"]
}
```

This is Terraform, so I didn't use the Ansible skill.

**Proposed fix:** take the allowed ranges as a required variable with no default, and reject `0.0.0.0/0` in validation.

```hcl
variable "ssh_allowed_cidrs" {
  description = "CIDR blocks allowed to reach the bastion over SSH (e.g. office or VPN egress ranges)"
  type        = list(string)

  validation {
    condition     = !contains(var.ssh_allowed_cidrs, "0.0.0.0/0")
    error_message = "ssh_allowed_cidrs must not contain 0.0.0.0/0."
  }
}

resource "aws_security_group" "bastion" {
  name = "bastion"

  ingress {
    description = "SSH from trusted ranges"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.ssh_allowed_cidrs
  }
}
```

**Other issues I noticed:**
- **No egress rule:** Terraform removes the default allow-all egress, so the bastion can't open outbound connections, including to the hosts it's meant to reach. Add an explicit egress rule, ideally limited to the target security groups or CIDRs.
- **No `vpc_id`:** The group will land in the default VPC. That is probably not what you want for a bastion.
- **IPv6:** There's no `ipv6_cidr_blocks`. If you add one later, apply the same restriction.
- **Better options than open SSH:** SSM Session Manager or EC2 Instance Connect Endpoint would let you drop inbound port 22 entirely.

I need the actual CIDRs to allow, such as your office or VPN egress ranges. Once I have them, or if you re-enable Write, I'll apply the change and run `terraform fmt` and `terraform validate`.
