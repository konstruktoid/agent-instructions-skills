I reviewed `infra/main.tf`. I couldn't apply the fix: I only have read/search tools in this session, so nothing has been edited and I haven't run `terraform validate` or `plan`.

## Findings

**1. SSH is open to the whole internet (`infra/main.tf:8`)**
`cidr_blocks = ["0.0.0.0/0"]` on port 22 lets anyone on the internet try to log in to the bastion. That invites constant brute-force attempts and leaves you exposed to any sshd vulnerability. This is the main issue.

**2. No `vpc_id`**
Without it, the group is created in the region's default VPC. That's probably not where the bastion is meant to live, and the group can't be attached to instances in other VPCs.

**3. No egress rule**
Unlike the AWS console, Terraform deletes the default allow-all egress rule. As written, the bastion has no outbound traffic at all, so it can't reach private hosts on port 22, which is the whole point of a bastion. If it works today, something else is allowing the traffic.

**4. No `description`**
It defaults to "Managed by Terraform". Changing it later forces the group to be destroyed and recreated, so set it now.

## Suggested change

```hcl
variable "vpc_id" {
  type = string
}

variable "ssh_allowed_cidrs" {
  description = "CIDRs allowed to SSH to the bastion (e.g. office/VPN egress IPs)"
  type        = list(string)
  # No default on purpose: callers must choose the ranges explicitly.

  validation {
    condition     = length(var.ssh_allowed_cidrs) > 0 && !contains(var.ssh_allowed_cidrs, "0.0.0.0/0")
    error_message = "ssh_allowed_cidrs must be non-empty and must not contain 0.0.0.0/0."
  }
}

variable "private_cidr" {
  description = "CIDR of the private subnets the bastion connects to"
  type        = string
}

resource "aws_security_group" "bastion" {
  name        = "bastion"
  description = "Bastion host SSH access"
  vpc_id      = var.vpc_id

  ingress {
    description = "SSH from trusted networks"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.ssh_allowed_cidrs
  }

  egress {
    description = "SSH to private hosts"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.private_cidr]
  }
}
```

- **What to set:** I don't know which ranges should have access. Fill in `ssh_allowed_cidrs` with your office or VPN egress IPs as `/32` addresses or small ranges.
- **Egress:** If the bastion also needs outbound HTTPS for package updates, add a 443 egress rule.
- **Rollout:** Adding `vpc_id` to a group that already exists forces Terraform to replace it. Check `terraform plan` before applying, and consider adding `lifecycle { create_before_destroy = true }`.
- **Stronger option:** If you can use AWS Systems Manager Session Manager, you can drop the port 22 ingress rule entirely. Access is then controlled through IAM and logged, with no open port.
- **Newer style:** Recent AWS provider versions recommend separate `aws_vpc_security_group_ingress_rule` and `aws_vpc_security_group_egress_rule` resources over inline blocks. That's optional, and worth doing only if the rest of your code uses that pattern.

Once you've chosen the allowed CIDRs, run `terraform fmt`, `terraform validate` and `terraform plan` to confirm the change does what you expect.
