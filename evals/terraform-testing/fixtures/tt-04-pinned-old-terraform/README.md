# owned-resource

A module that records which team owns a resource.

CI runs Terraform 1.5.7, pinned in `.terraform-version`, and the module supports Terraform 1.3 and
later. CI runs `make check` and nothing else, so anything that should be enforced must run from it.
