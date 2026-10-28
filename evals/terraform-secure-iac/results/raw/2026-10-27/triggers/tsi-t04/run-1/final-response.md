I couldn't make the fix, for two reasons.

**1. The workspace doesn't contain what the request describes.** The only Terraform file is `infra/main.tf`, and it holds a single `aws_security_group` resource. I found no `module` blocks, so there's no Git `source` missing a ref. There's also no `terraform { required_providers { ... } }` block, so there are no provider constraints to tighten. I searched for `**/*.tf*` and that one file was the only match.

**2. I can't edit files in this session.** I only have read and search tools, with no way to write files or run commands. So I also couldn't run `terraform fmt`, `validate` or `tflint`.

**Something I noticed while looking:** `infra/main.tf:8` allows SSH (port 22) in from `0.0.0.0/0`, meaning anyone on the internet can reach the bastion on that port. That's a real exposure, though it's not what you asked about.

**What I'd need to continue:**
- The path to the files that contain the `module` blocks, or the module source URLs.
- File-editing access, or you can apply the changes yourself. Here's what they would look like:
  ```hcl
  module "example" {
    # Pin to a full commit SHA (or a protected tag); HTTPS/SSH, no credentials in the URL
    source = "git::https://github.com/<org>/<repo>.git//<path>?ref=<40-char-commit-sha>"
  }

  terraform {
    required_version = "~> 1.9.0"
    required_providers {
      aws = {
        source  = "hashicorp/aws"  # confirm the expected namespace
        version = "= 5.x.y"        # or "~> 5.x.0", with .terraform.lock.hcl committed
      }
    }
  }
  ```
  After those edits, run `terraform providers lock -platform=linux_amd64 -platform=darwin_arm64` (plus any other platforms your CI uses) so the lock file records checksums for each. Then commit `.terraform.lock.hcl`.
