I didn't change anything, because there are no module sources or provider constraints in this workspace to fix.

**What I found**

- The only Terraform file is `infra/main.tf`. It has one resource, `aws_security_group.bastion`, and nothing else: no `module` blocks, no `terraform { required_providers { ... } }` block and no `provider` blocks.
- I searched the whole workspace for `module`, `source =`, `required_providers`, `git::` and `.git`, and found no matches. That includes the CI files (`.github/workflows/deploy.yml`, `.gitlab-ci.yml`, `Jenkinsfile`).
- There's no `.terraform.lock.hcl`.

So the Git module source with no ref doesn't exist in this checkout. It may be on another branch, in another directory or repository, or in files not committed yet. I also didn't have file-editing or shell tools in this session, so I couldn't have made changes or run `terraform fmt`, `validate` or `tflint` either way.

**If you point me at the right files**, the fix would look like this:

```hcl
terraform {
  required_version = "~> 1.9"  # match your toolchain

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.80"      # bounded; the lock file pins the exact build
    }
  }
}

module "network" {
  # Pin to a full commit SHA. A tag works only if the host stops it being moved.
  source = "git::https://github.com/example-org/terraform-aws-network.git?ref=<40-char-commit-sha>"
}
```

After that, run `terraform providers lock -platform=linux_amd64 -platform=darwin_arm64` (one `-platform` for each system CI and developers use) and commit `.terraform.lock.hcl`.

**A separate problem in `infra/main.tf`:** lines 4–9 open SSH (port 22) to `0.0.0.0/0`, so the bastion accepts SSH from the whole internet. You didn't ask about this, so I left it alone. It's worth narrowing to known address ranges, or replacing with SSM Session Manager.
