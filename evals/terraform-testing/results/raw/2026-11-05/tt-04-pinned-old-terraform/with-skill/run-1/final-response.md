I added the `full_name` output and a test for it that runs as part of `make check`. `make check` passes locally on Terraform 1.17.1. I couldn't run it on CI's 1.5.7, because only 1.17.1 is installed here. I didn't run `tflint`, which isn't installed and has no config in the repo.

- **Output:** `full_name` in `outputs.tf` is `"${var.team}-${var.name}"`, with a description.
- **Why not `terraform test`:** it needs Terraform 1.6 or later, and CI is pinned to 1.5.7 while the module supports 1.3. I used a plan-and-assert script instead, in `tests/full_name.sh`. It plans the module, reads the planned output as JSON with `jq`, and compares it to the expected string.
- **What it checks:**
  - `platform` + `web` gives `platform-web`.
  - Inputs that already contain hyphens (`a-b` + `c-d`) are joined without losing them.
  - A plan with no `name` fails.
- **CI wiring:** I added the script as the last step of `make check` in the `Makefile`. CI runs only that target. The script needs `jq`, so the CI image must have it.
- **Test fails without the change:** I changed the join to an underscore and `make check` failed with `expected 'platform-web', got 'platform_web'`. I then restored the hyphen, and `make check` passes again. While reverting I accidentally wiped the output with `git checkout` and re-added it, so `outputs.tf` is correct now.
- **Cleanup:** the script plans into a temp directory and deletes it, and nothing is applied. I removed `.terraform/` and the lock file, so the tree has only the intended changes: `Makefile`, `outputs.tf` and `tests/`.

I didn't commit anything.
