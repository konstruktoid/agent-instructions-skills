# service-endpoint

A module that records one service and the address clients use to reach it.

## Tests

The tests are Terratest tests under `test/`, with their own `go.mod`. Run them from that directory.

- `test/unit/` holds one file per output, named for it, and every test plans and reads the planned
  values without applying. `go test ./unit/...` runs them.
- `test/integration/` holds tests that apply. They carry the `integration` build tag and CI runs
  them in a sandbox account, so nobody adds to them without the platform team.
