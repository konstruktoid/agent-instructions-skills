I added the `full_name` output and a test for it that runs as part of `make check`. `make check` passes. With the output's join order swapped as a check, it fails with `FAIL: team=platform name=web: full_name=web-platform, want platform-web`.

- **Output:** `outputs.tf` now has `full_name`, which is `"${var.team}-${var.name}"`.
- **Test:** `tests/full_name.sh` is new. It plans the module for two team/name pairs, `platform` + `web` and `data` + `etl-job`. It reads the planned `full_name` from the plan JSON with `jq` and compares it to the expected value. It only plans, so it creates nothing. The plan file lives in a temp directory that is removed on exit.
- **Makefile:** `make check` now runs `tests/full_name.sh` after `terraform validate`. CI runs only `make check`, so the test is enforced there.

I used a shell script instead of native `terraform test` because CI is pinned to Terraform 1.5.7 and the module supports 1.3 and later. Native `terraform test` needs 1.6 or later. I ran the suite locally with Terraform 1.17.1, not 1.5.7, because that is the version installed here. The script only uses `plan`, `show -json` and `jq`, which 1.5.7 also has, but I haven't run it on 1.5.7.

There is no `.tflint.hcl` and `tflint` isn't installed, so I didn't run it. I didn't add any input validation, because the request didn't ask for it.
