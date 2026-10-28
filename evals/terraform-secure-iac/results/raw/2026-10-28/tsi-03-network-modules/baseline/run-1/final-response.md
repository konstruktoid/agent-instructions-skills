I made the changes, but I couldn't run `terraform init` or `validate`, so none of it has been checked beyond `terraform fmt`. `init` failed because `git.example.com`, the source of the existing `labels` module, doesn't resolve from this environment. That module is unpinned, and I left it as it was.

- **`versions.tf`:** the AWS provider constraint changes from `>= 4.0` to `~> 6.0`. The S3 backend block is untouched.
- **`main.tf`:** there is a new `module "vpc"` using `terraform-aws-modules/vpc/aws`, pinned to `~> 6.0`.
  - It is named `network-<environment>`.
  - It has two private subnets, in `eu-north-1a` and `eu-north-1b`. The zones are built from `var.region`.
  - DNS support and DNS hostnames are on.
  - NAT gateways are off, so the subnets have no outbound internet. Say if you want NAT added.
  - It gets `tags = module.labels.tags`. The provider's `default_tags` already use the same tags, so everything is tagged through the labels module.
- **`variables.tf`:** two new variables, `vpc_cidr` (default `10.0.0.0/16`) and `private_subnet_cidrs` (defaults `10.0.1.0/24` and `10.0.2.0/24`). I picked those CIDRs, so check they don't overlap anything you already use.

Run `terraform init -upgrade && terraform plan` somewhere that can reach the labels repo. Moving from provider 4.x/5.x to 6.x can change existing resources, and this config has none, but the state may. I also didn't commit anything.
