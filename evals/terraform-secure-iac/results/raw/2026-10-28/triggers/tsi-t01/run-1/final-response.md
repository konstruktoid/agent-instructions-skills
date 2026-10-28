I couldn't change any files. This session can only read and search files, so I can't edit or run commands. The block below is ready to add, but nothing has been written to the repo and I haven't run `fmt`, `validate` or `tflint`.

## Add to `infra/main.tf` (or a new `infra/backend.tf`)

```hcl
terraform {
  required_version = ">= 1.10.0"

  backend "s3" {
    key          = "infra/terraform.tfstate"
    encrypt      = true
    use_lockfile = true
  }
}
```

Put the per-environment settings in a file passed at init (`terraform init -backend-config=backend.hcl`):

```hcl
# backend.hcl — not secret, can be committed or generated in CI
bucket     = "<state-bucket-name>"
region     = "<region>"
kms_key_id = "<kms-key-arn-or-alias>"
```

Why it's set up this way:
- **`use_lockfile = true`** uses S3's built-in locking, so two people can't apply at the same time. You don't need a DynamoDB table, but it requires Terraform 1.10 or newer, hence `required_version`.
- **`encrypt` with a KMS key** encrypts the state at rest with a key you control. State files hold every resource attribute, including secrets, in plaintext.
- **No credentials in the block.** Everyone authenticates with their normal AWS identity (SSO or a role). Don't put `access_key` or `secret_key` here or in `backend.hcl`.
- **The bucket and key are kept out of the main config.** That way the same code works for each environment without hardcoding account details.

## The bucket itself needs
- Versioning turned on, so you can recover from a bad write or a corrupted state.
- Block Public Access fully on, and a bucket policy that denies requests not using HTTPS.
- Default SSE-KMS encryption, with key access limited to the people and CI roles that run Terraform.
- Its own setup, separate from this root. If this root manages the bucket, you can't initialise the backend before the bucket exists.

## Migrate
Pick one person with the latest copy of the state, then:
1. `terraform init -backend-config=backend.hcl -migrate-state`
2. `terraform plan`. It should show no changes.
3. Delete the local `terraform.tfstate` and `*.backup` files.
4. Add `*.tfstate`, `*.tfstate.*` and `.terraform/` to `.gitignore`.

## Two other things to fix
- **The state shared over Slack should be treated as leaked.** Anything sensitive in it, like passwords or keys from your resources, is now in Slack's history. Rotate those values and delete the files from Slack.
- **`infra/main.tf:8` opens SSH (port 22) on the bastion to the whole internet (`0.0.0.0/0`).** This isn't part of the backend change, but you should restrict it to known address ranges or replace SSH with SSM Session Manager.

Once you've added the block, run `terraform fmt -recursive -check -diff`, then `terraform init -backend=false && terraform validate`, then `tflint` to check it.
