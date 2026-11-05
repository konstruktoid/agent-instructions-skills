I added a `full_name` output in `outputs.tf`, defined as `"${var.team}-${var.name}"`, and extended `make check` to test it.

- **New check:** `make check` now applies the module with `team=alpha` and `name=web`. It then fails unless `full_name` is `alpha-web`. It writes its state to `.terraform/check.tfstate`, so nothing is left in the repo root.
- **Why not `terraform test`:** CI is pinned to Terraform 1.5.7 and the module supports 1.3 and later, and `terraform test` needs 1.6 or newer. The apply-and-compare approach uses only commands available in 1.5.7.
- **Results:** `make check` passes. To confirm the check can fail, I temporarily set the expected value to `wrong`, and it failed as expected. I then restored `alpha-web` and it passed again.
- **Not tested on 1.5.7:** I ran it with the locally installed Terraform 1.17.1, not 1.5.7.
- **Untracked `.terraform/`:** `terraform init` created it, and there's no `.gitignore` in the repo. You may want to add one.
