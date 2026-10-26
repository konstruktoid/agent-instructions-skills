# reports

Terraform for the reports bucket and the key the nightly export job uploads with. The job reads
the key from `terraform output`.

## Usage

```sh
terraform init
terraform apply
```

State is kept locally in `terraform.tfstate`, so only the person who last ran `apply` has it.
