I couldn't apply the change because the Edit tool is disabled in this session, so `infra/main.tf` is unchanged. Nothing has been run or verified. The only file in the module is `infra/main.tf`, and the problem is the ingress rule on lines 4–9, which opens SSH to `0.0.0.0/0`.

Here is the change I would make:

```hcl
variable "ssh_allowed_cidrs" {
  description = "CIDR blocks allowed to reach the bastion over SSH"
  type        = list(string)

  validation {
    condition     = !contains(var.ssh_allowed_cidrs, "0.0.0.0/0")
    error_message = "ssh_allowed_cidrs must not contain 0.0.0.0/0."
  }
}

resource "aws_security_group" "bastion" {
  name = "bastion"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.ssh_allowed_cidrs
  }
}
```

- **No default:** The variable has no default, so callers have to name the CIDRs (an office or VPN range, for example). I didn't want to guess your addresses.
- **Validation:** The validation block stops anyone from putting `0.0.0.0/0` back later.

Other things I noticed in the module:
- **No egress rule:** Terraform removes AWS's default allow-all egress, so the bastion can't make outbound connections. If it needs to reach private hosts, add an egress rule for that.
- **No `vpc_id`:** The group will go into the default VPC. That is probably not what you want for a bastion.
- **Better than IP allowlists:** SSM Session Manager would let you drop port 22 entirely.

If you want me to apply the edit, enable Edit or tell me to write the file another way. Tell me the CIDRs to allow and I'll add a `terraform.tfvars` example. After the change, run `terraform fmt -check` and `terraform validate`.
