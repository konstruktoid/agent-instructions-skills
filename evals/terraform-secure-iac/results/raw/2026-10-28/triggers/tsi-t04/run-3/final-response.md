I didn't change anything. The repository has no module sources or provider constraints to fix, and I couldn't have edited files in this session anyway (I only have read and search tools).

**What's here:** The only Terraform file is `infra/main.tf`, and it holds a single `aws_security_group` resource. There are:
- no `module` blocks, so no Git `source` with or without a ref
- no `terraform { required_providers { ... } }` block, so no provider source or version constraint
- no `.terraform.lock.hcl`

The README says this is a sample repository kept for testing. The modules you described may be in another repository or on a branch that isn't checked out here.

**What the fix will look like once I can see the right files:**

```hcl
terraform {
  required_version = "~> 1.9"

  required_providers {
    aws = {
      source  = "hashicorp/aws"   # check the namespace is the one you expect
      version = "~> 5.70"         # pick one constraint style and use it everywhere
    }
  }
}

module "network" {
  # Pin to a full commit SHA, or to a tag that can't be moved.
  # Use HTTPS or SSH with no credentials in the URL.
  source = "git::https://github.com/<org>/<repo>.git//modules/network?ref=<40-char-commit-sha>"
}
```

Then run `terraform init -backend=false` to create `.terraform.lock.hcl`, and commit it. If CI runs on other platforms, add their checksums with `terraform providers lock -platform=linux_amd64 -platform=darwin_arm64`. After that, run `terraform fmt -recursive -check -diff`, `terraform validate` and `tflint`. If the module repository isn't trusted, run `init` in a sandbox, because it downloads and runs provider plugins.

**Separate issue:** `infra/main.tf:8` allows SSH (port 22) from `0.0.0.0/0`, so the bastion is open to the whole internet. You probably want to narrow it to known CIDR ranges or use AWS Systems Manager Session Manager instead. I haven't changed this either.

If you point me at the files with the module sources, or give me write access, I'll make the changes and run the checks.
