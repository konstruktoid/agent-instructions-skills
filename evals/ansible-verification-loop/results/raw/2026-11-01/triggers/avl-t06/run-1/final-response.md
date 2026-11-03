I couldn't change the file because this session gives me only read and search tools, with no edit or shell access. Below is my review and the exact change I'd make. I haven't run `terraform validate` or `plan` on it.

## Review of `infra/main.tf`

**1. SSH is open to the whole internet (`infra/main.tf:8`).** `cidr_blocks = ["0.0.0.0/0"]` on port 22 lets any IPv4 address try to log in, so the bastion will get constant brute-force and scanning traffic. This is the main problem.

**2. The security group has no outbound access.** With the `aws_security_group` resource, if you write no `egress` block, Terraform removes AWS's default allow-all outbound rule. A bastion has to SSH out to private hosts, so as written it probably can't do its job. If it works today, someone may have added an outbound rule by hand, and Terraform would delete it on the next apply. I'd check this before applying.

**3. `vpc_id` isn't set.** The group lands in the default VPC, which is rarely the right place for a bastion.

**4. Minor issues:**
- There's no `description` on the group or the rule.
- Inline `ingress` blocks are harder to manage than separate `aws_vpc_security_group_ingress_rule` resources, which the AWS provider now recommends.

## Proposed change

The allowed source addresses become a required variable, with a check that rejects open-to-the-world values:

```hcl
variable "ssh_allowed_cidrs" {
  description = "CIDR blocks allowed to SSH to the bastion (e.g. office/VPN egress IPs)."
  type        = list(string)

  validation {
    condition = length(var.ssh_allowed_cidrs) > 0 && alltrue([
      for c in var.ssh_allowed_cidrs : can(cidrhost(c, 0)) && !contains(["0.0.0.0/0", "::/0"], c)
    ])
    error_message = "ssh_allowed_cidrs must be non-empty, valid CIDRs, and must not include 0.0.0.0/0 or ::/0."
  }
}

resource "aws_security_group" "bastion" {
  name = "bastion"

  ingress {
    description = "SSH from approved networks"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.ssh_allowed_cidrs
  }
}
```

Then set the real ranges in a tfvars file, for example `ssh_allowed_cidrs = ["203.0.113.10/32"]` for your office or VPN address.

Changing `cidr_blocks` updates the existing rule in place. I left `vpc_id` and the group's `description` out on purpose: changing either one destroys and recreates the security group, which would disrupt anything attached to it. If you want those, make them a separate, planned change.

## Decisions for you
- **Which addresses should be allowed?** Your office, VPN or CI addresses, as `/32` where possible.
- **Do you need port 22 open at all?** You could replace SSH with AWS Systems Manager Session Manager and remove the inbound rule completely.
- **Outbound rules:** add an `egress` rule limited to port 22 toward your private subnets' address ranges, because of issue 2.

If you enable file editing, I can apply this and run `terraform fmt`, `terraform validate` and `terraform plan` to confirm the rule is updated in place rather than the group being replaced.
