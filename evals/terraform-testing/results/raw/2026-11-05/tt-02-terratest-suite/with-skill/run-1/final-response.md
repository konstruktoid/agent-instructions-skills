The endpoint output now renders as `https://HOST:PORT`, and a new unit test fails if the `/` comes back.

- **Fix:** in `outputs.tf`, `"https://${var.host}/${var.port}"` is now `"https://${var.host}:${var.port}"`.
- **Test:** `test/unit/endpoint_test.go` is a new Terratest test. It follows the repo's existing layout of one file per output and a plan-only run, so it applies nothing. It checks the default port (`https://api.example.internal:8443`) and a custom port (`https://api.example.internal:9000`).
- **Results:**
  - `go test ./unit/...` passes, including the existing `TestServiceName`.
  - With the fix reverted, the new test fails with `https://api.example.internal/8443` where it expected `:8443`. So it is testing the fix.
  - `terraform fmt -check` is clean.
  - No state, plan or `.terraform` files were left in the tree.
  - I didn't run `tflint` or the integration tests. The integration tests apply real infrastructure and are meant to run in CI, not here.
- **Go dependencies:** `test/go.sum` was missing, so no unit test could build, including the existing one. I ran `go mod tidy` to fix that. It added `test/go.sum` and a large block of indirect dependencies to `test/go.mod`, which you'll want to review and commit. `go mod tidy` downloaded those modules from the network.
- **Build flag:** the default linker hit a disk-quota error in this sandbox, so I ran the tests with `-ldflags='-s -w'`. You shouldn't need that flag elsewhere.

I haven't committed anything.
