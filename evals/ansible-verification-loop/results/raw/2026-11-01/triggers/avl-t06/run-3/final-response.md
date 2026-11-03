I reviewed `infra/main.tf`. It's the only Terraform file in the workspace. I couldn't edit it because I only have read and search tools in this session, so the fix is below for you to apply. Nothing has been run against it (`terraform validate`, `plan`, etc.).

## Findings

1. **SSH is open to the whole internet** (`infra/main.tf:8`). `cidr_blocks = ["0.0.0.0/0"]` on port 22 lets anyone reach the bastion, which invites brute-force attempts and attacks on any sshd vulnerability.
2. **The bastion has no outbound traffic.** When Terraform creates an `aws_security_group`, it removes AWS's default allow-all egress rule. With no `egress` block, the bastion can't reach the instances behind it. That breaks SSH forwarding and `ProxyJump`, which a bastion exists to do. You may not have noticed yet if nothing has been applied.
3. **No `vpc_id`**, so the group lands in the default VPC. That's probably not what you want for a bastion.
4. **No `description`.** It defaults to "Managed by Terraform", and changing it later forces the group to be replaced, so it's best to set it now.

## Suggested change

Make the allowed CIDRs a required variable, and add a check that rejects open-to-the-world ranges so `0.0.0.0/0` can't come back by accident:

```hcl
variable "vpc_id" {
  type        = string
  description = "VPC the bastion lives in."
}

variable "ssh_allowed_cidrs" {
  type        = list(string)
  description = "CIDRs allowed to SSH to the bastion (e.g. office/VPN egress IPs)."

  validation {
    condition = length(var.ssh_allowed_cidrs) > 0 && alltrue([
      for c in var.ssh_allowed_cidrs : can(cidrnetmask(c)) && !contains(["0.0.0.0/0"], c)
    ])
    error_message = "ssh_allowed_cidrs must be non-empty, valid IPv4 CIDRs, and must not include 0.0.0.0/0."
  }
}

variable "internal_cidrs" {
  type        = list(string)
  description = "Private ranges the bastion may SSH onward to."
}

resource "aws_security_group" "bastion" {
  name        = "bastion"
  description = "SSH bastion - restricted ingress"
  vpc_id      = var.vpc_id

  ingress {
    description = "SSH from trusted networks"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.ssh_allowed_cidrs
  }

  egress {
    description = "SSH onward to internal hosts"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.internal_cidrs
  }
}
```

Notes:
- **Picking the CIDRs:** use your office or VPN egress IPs as `/32`s, or a small range. If your admins' IPs change often, an AWS managed prefix list (`prefix_list_ids`) is easier to maintain than hard-coded CIDRs.
- **Egress:** if the bastion also needs package updates, add a 443 egress rule, ideally to a NAT gateway or VPC endpoints.
- **Adding `description` or `vpc_id` replaces the group.** Terraform will destroy and recreate it, which can cause a short outage or fail if instances still use it. Add `lifecycle { create_before_destroy = true }` or plan the change for a quiet window.
- **A bigger option:** AWS SSM Session Manager would let you remove the port-22 ingress completely and drop the public IP.

After applying, run `terraform fmt`, `terraform validate` and `terraform plan`, and check that the plan shows the ingress change you expect.
