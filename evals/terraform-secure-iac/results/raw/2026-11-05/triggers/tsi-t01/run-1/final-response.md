I couldn't add the backend block because the Write tool is disabled in this session, so I haven't changed any files. I also couldn't read the skill's `references/state.md`, because read permission for it wasn't granted. The block below follows general S3 backend practice instead.

The root is `infra/main.tf`, which only has a bastion security group and no existing `terraform` block. I would add this as `infra/backend.tf`:

```hcl
terraform {
  required_version = ">= 1.10"

  # Bucket, key, and region are supplied at init time so no environment-specific
  # values live in the repository:
  #   terraform init -backend-config=backend.hcl
  # Credentials come from the environment or an assumed role, never from this block.
  backend "s3" {
    encrypt      = true
    use_lockfile = true
  }
}
```

- **Why `-backend-config`:** a backend block can't use variables, so leaving `bucket`, `key` and `region` out keeps real account details out of git. Keep `backend.hcl` out of git unless it holds only non-secret values.
- **Locking:** `use_lockfile` does S3-native locking and needs Terraform 1.10 or later. On an older version, use a `dynamodb_table` instead.
- **Bucket requirements:** the bucket needs versioning, default encryption (SSE-KMS preferred), a public-access block, a bucket policy limited to the team's roles, and TLS-only access. Create it outside this root so it doesn't depend on its own state.
- **Migrating existing state:** run `terraform init -migrate-state`. Then delete any local `terraform.tfstate` files and the copies shared over Slack, because state can contain secrets. Make sure `*.tfstate*` is in `.gitignore`.
- **Not run:** I ran none of `terraform fmt`, `terraform init -backend=false`, `terraform validate` or `tflint`.

Separately, the security group in `infra/main.tf` opens SSH to `0.0.0.0/0`, which a scanner will flag. I left it alone because it's outside this request.

If you re-enable Write, or tell me to use another way to edit, I'll add the file. Tell me the bucket name, region and key path and I'll also write the `backend.hcl` template.
