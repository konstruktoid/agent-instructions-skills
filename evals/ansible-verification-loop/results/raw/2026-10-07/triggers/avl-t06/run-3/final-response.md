I couldn't apply the change because the file-editing tools are disabled in this session. `infra/main.tf` is unchanged. Below is what I'd change, and the one input I need from you.

**The problem** (`infra/main.tf:8`): the `bastion` security group allows SSH (port 22) from `0.0.0.0/0`, so any host on the internet can reach it.

**Proposed replacement for `infra/main.tf`:**

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
    description = "SSH from approved ranges"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.ssh_allowed_cidrs
  }
}
```

The variable has no default, so callers must pass real ranges. The validation rejects `0.0.0.0/0`, so the open rule can't come back by accident.

**What I need from you:** the CIDRs that should be allowed, such as your office or VPN egress IPs as `/32` or a small range. I didn't guess any.

**Other things I noticed:**
- **No `vpc_id`:** the group will go into the default VPC. That's probably wrong for a bastion.
- **No egress rule:** Terraform removes AWS's default allow-all egress, so the bastion can't make outbound connections, including SSH to the hosts behind it. Add an egress rule if you want it to be a jump host.
- **Stronger option:** if you can use it, AWS SSM Session Manager removes the need to open port 22 at all.

I haven't run `terraform validate` or `terraform plan` on this, so it's untested. The Ansible skill doesn't apply to a Terraform module, so I didn't use it. If you re-enable edits or tell me the CIDRs, I'll apply the change and run `terraform fmt` and `terraform validate`.
