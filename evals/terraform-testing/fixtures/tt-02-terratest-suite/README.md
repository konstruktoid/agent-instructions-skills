# service-endpoint

A module that records one service and the address clients use to reach it.

The tests are Terratest tests under `test/`. Run them from that directory with `go test ./...`.
The module creates only `terraform_data`, so applying it provisions nothing outside Terraform state.
