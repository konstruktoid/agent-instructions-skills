I added a `full_name` output in `outputs.tf`, and `make check` now tests it. The value is `"${var.team}-${var.name}"`.

`make check` passes. I also changed the expected value to a wrong one, and `make check` then failed with "Resource precondition failed", so the check does catch a bad `full_name`.

- **How it's tested:** CI pins Terraform 1.5.7, and `terraform test` only exists from 1.6. So I added `tests/full_name/main.tf` instead. It calls the module with `platform` and `db`, and a resource precondition requires `full_name` to equal `platform-db`. The Makefile now ends with a `terraform init` and `terraform plan` in that directory.
- **Version caveat:** I ran this on the Terraform installed here, which is 1.17.1, not 1.5.7. The precondition syntax has been supported since 1.2, so it should work on 1.5.7, but I haven't run it there.

I haven't committed anything.
