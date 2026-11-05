I couldn't add the S3 backend block. The Write tool is disabled in this session, so nothing in the repo has changed, and I haven't run `terraform fmt`, `validate` or `tflint`.

I also couldn't read the skill's `references/state.md`, because the read permission was denied. What follows comes from general practice, not from that file.

Here is the block I meant to put in `infra/backend.tf`. There is currently no `terraform {}` block anywhere in the repo.

```hcl
terraform {
  # use_lockfile (S3-native locking) requires Terraform 1.10 or later.
  required_version = ">= 1.10"

  # Partial configuration: bucket, key and region are supplied at init time so
  # no account-specific values are committed.
  backend "s3" {
    encrypt      = true
    use_lockfile = true
  }
}
```

- **Init command:** each person would run `terraform init -backend-config=backend.hcl`. That file holds only the bucket, key and region. Don't put credentials in it. Credentials should come from the environment or an assumed role.
- **Bucket requirements:** the bucket needs versioning, default encryption (SSE-KMS preferred), and public access blocked. Access should be limited to a narrow IAM role for the team.
- **Existing state:** if anyone already has a local state file, run `terraform init -migrate-state` once. Then delete the copies that were shared over Slack. Those copies may contain secrets.
- **Gitignore:** make sure `*.tfstate*`, `*.tfplan` and `backend.hcl` (if you'd rather not commit it) are in `.gitignore`.

Separately, `infra/main.tf:8` opens SSH on the bastion security group to `0.0.0.0/0`. You should restrict that to known CIDRs or use SSM Session Manager.

If you re-enable Write or grant the permissions, I'll create the file, add the `.gitignore` entries and run the checks.
