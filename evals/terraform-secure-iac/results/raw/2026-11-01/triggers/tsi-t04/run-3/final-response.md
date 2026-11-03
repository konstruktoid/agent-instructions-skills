I didn't change anything. This repository has no module sources and no provider constraints to fix.

**What's here:** `infra/main.tf` is the only Terraform file. A search for `source =`, `version =` and `required_version` across the whole workspace found nothing. The file holds one resource, `aws_security_group.bastion`. It has no `module` blocks, no `terraform { required_providers }` block and no `.terraform.lock.hcl`. Whatever has the unpinned Git module source must be in another repository or branch.

**Two things are worth fixing in this repo anyway:**

1. **The provider isn't pinned.** Because `aws` is never declared, Terraform installs whatever the latest `hashicorp/aws` release is. A pinned version would look like this:
   ```hcl
   terraform {
     required_version = "~> 1.9"
     required_providers {
       aws = {
         source  = "hashicorp/aws"
         version = "= 5.x.y" # set to the exact release you've tested
       }
     }
   }
   ```
   Then run `terraform init` and commit `.terraform.lock.hcl`. If CI runs on other platforms, add their checksums with `terraform providers lock -platform=linux_amd64 -platform=darwin_arm64`.

2. **SSH is open to the whole internet.** Port 22 accepts connections from `0.0.0.0/0` (`infra/main.tf:8`). That's a bigger exposure than the missing pin. Limit it to a known admin CIDR, or use SSM Session Manager and drop the rule.

**For the Git module sources, once I can see them:** pin each one to a full commit SHA. A tag only works if it's protected against being moved. Use HTTPS or SSH with no credentials in the URL, for example:
```hcl
source = "git::https://github.com/org/repo.git//modules/x?ref=<40-char-sha>"
```

**Limits of this session:** I only have read and search tools here, no file editing or shell. So I couldn't make the edits or run `terraform fmt`, `validate` or `tflint`. If you point me to the repository with the modules and give me edit and shell access, I'll pin the sources and run those checks.
