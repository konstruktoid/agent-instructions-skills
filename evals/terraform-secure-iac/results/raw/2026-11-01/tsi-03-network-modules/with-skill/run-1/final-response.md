The AWS provider is now on the 6.x line and the VPC is added, but I couldn't run `terraform validate` or tflint. The internal labels module lives at `git.example.com`, which this sandbox can't reach, so `terraform init` fails before validate can run. tflint isn't installed here.

**What I changed**
- **Provider:** `versions.tf` now pins `hashicorp/aws` to `~> 6.0` (it was `>= 4.0`). I also added `required_version = ">= 1.10"`, which wasn't in your request. Say if you'd rather I drop it.
- **VPC:** the new `vpc.tf` uses `terraform-aws-modules/vpc/aws` at exactly `6.7.3`. It creates two private subnets, `10.0.1.0/24` in eu-north-1a and `10.0.2.0/24` in eu-north-1b, inside `10.0.0.0/16`.
- **No outbound route:** I set `enable_nat_gateway = false`, so the subnets have no route to the internet. Turn it on if you need that.
- **Variables:** `variables.tf` has three new variables for the VPC CIDR, the availability zones and the subnet CIDRs, all with those defaults.
- **Tagging:** the VPC module gets `tags = module.labels.tags`, and the provider's `default_tags` still applies the same tags. The VPC name is `network-${var.environment}`. I didn't use any labels output keys, because I couldn't see what the labels module exposes.

**Checks**
- `terraform fmt` is clean.
- checkov (the only scanner available) reports 2 passed and 3 failed:
  - Both the labels module and the VPC module were flagged for not being pinned to a commit hash.
  - The labels module was also flagged for not using a version-numbered tag.
  - I did not suppress anything.
  - The VPC module is pinned to an exact registry version; checkov's rule asks for a commit hash.
- The labels module's `git::https://git.example.com/platform/terraform-labels.git` source has no `?ref=`, so it follows the default branch. I didn't change it because I don't know which tag or SHA you want. Please give me one, or pin it yourself.
- There is no `.terraform.lock.hcl`. Once you can reach the labels host, run `terraform init`, then `terraform providers lock -platform=linux_amd64 -platform=darwin_arm64` (or whichever platforms CI and your developers use), and commit the file.
- Run `terraform plan` against the staging account to confirm the 6.x provider upgrade produces no unexpected changes. I haven't run one.

Nothing is committed.
