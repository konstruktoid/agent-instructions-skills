I couldn't edit anything. This session has no tool for writing files or running commands, so I haven't changed or checked anything in `infra/`. Here's the block to add as `infra/backend.tf`:

```hcl
terraform {
  required_version = ">= 1.10.0" # needed for S3-native locking (use_lockfile)

  backend "s3" {
    # Partial configuration: bucket, key, region and kms_key_id come from
    # -backend-config so no account-specific names live in the repository.
    encrypt      = true
    use_lockfile = true
  }
}
```

And an example settings file, `infra/backend.s3.tfbackend.example`:

```hcl
bucket     = "example-tfstate-bucket"
key        = "infra/terraform.tfstate"
region     = "eu-west-1"
kms_key_id = "alias/example-tfstate"
```

Each person copies the example to `backend.s3.tfbackend`, fills in the real values, and runs:

```sh
terraform -chdir=infra init -backend-config=backend.s3.tfbackend -migrate-state
```

The first person to run it should be whoever has the most recent copy of the state from Slack. `-migrate-state` uploads their local `terraform.tfstate` to S3. After that, delete the local copies and the Slack messages, because state can contain secrets.

**Why it's set up this way:**
- **Values kept out of the file:** Bucket and key names identify your account, so they stay out of the repo. Add `*.tfbackend`, `*.tfstate*`, `*.tfplan` and `.terraform/` to `.gitignore`.
- **Encryption:** `encrypt = true` turns on encryption at rest. With `kms_key_id` set, you control who can decrypt the state through the KMS key's policy.
- **Locking:** `use_lockfile = true` stops two people applying at the same time without needing a DynamoDB table. It requires Terraform 1.10 or later. On an older version, use `dynamodb_table` instead.

**The bucket has to provide the rest. The backend block can't:**
- Versioning turned on, so a bad apply or a corrupted state can be rolled back.
- Block Public Access turned on, with a bucket policy that denies non-TLS requests.
- Access limited to the team or CI roles that run Terraform.

Create the bucket outside this root, either in a small bootstrap config or by hand. Otherwise this root would be storing its state in a bucket it manages itself.

**Not done:**
- I didn't run `terraform fmt`, `terraform init -backend=false`, `terraform validate` or `tflint`.
- I couldn't read the skill's `references/state.md` because permission was denied, so the advice above is general practice rather than taken from that file.

**Separate problem:** `infra/main.tf:8` opens SSH (port 22) on the bastion to `0.0.0.0/0`, which means anyone on the internet. It should be limited to known address ranges, or replaced with SSM Session Manager. I left it unchanged because it isn't part of this request.
