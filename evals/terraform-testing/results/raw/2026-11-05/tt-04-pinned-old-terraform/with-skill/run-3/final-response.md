I added the `full_name` output and a check for it that `make check` runs. `make check` passes, and the new check fails when I break the output.

- **Output:** `outputs.tf` now has `full_name`, which is `"${var.team}-${var.name}"`, with a description.
- **Test:** the repo is pinned to Terraform 1.5.7 and CI only runs `make check`. Native `terraform test` needs 1.6 or later, so I used a plan-based check instead. `tests/full_name.sh` plans with two sets of inputs and reads the planned `full_name` with `jq`. The inputs are `platform`/`web`, which should give `platform-web`, and `a`/`b-c`, which should give `a-b-c`. It only plans, so it creates nothing, and its plan file is deleted when it finishes.
- **Wiring:** `Makefile` now runs `./tests/full_name.sh` after `validate`.
- **Revert check:** I temporarily changed the hyphen to an underscore. The script failed with `full_name=platform_web, want platform-web`. I then restored the hyphen.
- **Version caveat:** I ran this locally on Terraform 1.17.1, not 1.5.7. The script only uses `plan`, `show -json` and `planned_values.outputs`, which I expect 1.5.7 to support, but I haven't run it there.
- **Dependency:** the script needs `jq`, which is present locally. I didn't confirm it exists on the CI runner.
- **Extra file:** I added a `.gitignore` for `.terraform/`, state files and plan files. There wasn't one, and `make check` creates `.terraform/`.
- **Not run:** `tflint` isn't installed here and the repo has no `.tflint.hcl`, so I didn't run it.
- **Not done:** I didn't commit anything.
