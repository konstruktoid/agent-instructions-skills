I added a `full_name` output (`"${var.team}-${var.name}"`) in `outputs.tf`, and `make check` now covers it. `make check` passes locally, but only on Terraform 1.17.1. CI pins 1.5.7 and I couldn't run that version here.

- **The test:** `make check` now calls a new `test` target. It applies a small wrapper config in `tests/full_name/` with team `platform` and name `db`. It then fails unless the `full_name` output is `platform-db`.
- **Why not `terraform test`:** CI pins 1.5.7 and the module supports 1.3 and later, but `terraform test` needs 1.6 or later. The wrapper uses only `init`, `apply` and `output`, which exist in 1.5.7. I wrote it with that in mind but haven't run it there.
- **`.gitignore`:** I added one for `.terraform/`, state files and the lock file, so the test run leaves nothing to commit.

**Existing problem:** `main.tf` uses `terraform_data`, which needs Terraform 1.4 or later. `versions.tf` still says `>= 1.3.0`. I didn't change it, but it's probably worth bumping.

I haven't committed anything.
