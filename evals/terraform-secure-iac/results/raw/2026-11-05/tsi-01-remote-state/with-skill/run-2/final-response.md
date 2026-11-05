I added the `bootstrap/` configuration, pointed the backend at it and updated the README. I haven't applied anything or tried a real backend init, because there are no AWS credentials here. That also means the migration steps in the README are untested.

**What I ran**
- `terraform fmt -check` is clean and `terraform validate` passes in both the root and `bootstrap/`.
- `tflint` isn't installed here, so I didn't run it.
- `checkov` on `bootstrap/` passed 30 checks and failed 4: no cross-region replication, no event notifications, no access logging, and no explicit KMS key policy. I left those unfixed. The first three need extra buckets or destinations that you haven't asked for. The key uses AWS's default policy.
- I generated `.terraform.lock.hcl` for the root and for `bootstrap/` on linux and darwin, amd64 and arm64.

**What changed**
- **`bootstrap/`** creates the state bucket with:
  - versioning on, and old versions expiring after 90 days;
  - encryption with a new KMS key that has rotation on;
  - a public access block and a policy that denies non-TLS requests;
  - `prevent_destroy` on the bucket.
- **`backend.tf`** uses the S3 backend with `encrypt = true` and `use_lockfile = true`, so no DynamoDB table is needed. The bucket name is a placeholder, `example-reports-tfstate`. Replace it with the name you apply in `bootstrap/` before running `init`.
- **`.gitignore`** now excludes state, plan files and `.terraform/`.
- **README** now covers:
  - the one-time bootstrap;
  - the IAM and KMS permissions each engineer needs;
  - migrating the existing state with `terraform init -migrate-state`, then checking that `plan` shows no changes before deleting the laptop copy;
  - the day-to-day workflow with a saved plan.

**To be aware of**
- `bootstrap/` keeps its own state locally, and the README says to retain it with the team administrators.
- The existing state holds the uploader's secret access key through `aws_iam_access_key.uploader`. Remote encryption and access control reduce that exposure but don't remove it. I noted this in the README and left it as is, since changing it is outside this request.
