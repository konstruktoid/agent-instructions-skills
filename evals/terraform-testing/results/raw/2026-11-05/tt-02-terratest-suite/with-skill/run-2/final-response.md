The endpoint output now renders as `https://HOST:PORT`, and new tests lock it in. The unit suite passes with the fix. With the fix reverted, both new tests fail.

- **Fix:** `outputs.tf` now builds the endpoint as `https://${var.host}:${var.port}`. Before, it put a `/` between host and port.
- **Tests:** `test/unit/endpoint_test.go` is new. It follows the existing Terratest layout, with one file named for the output, planning only and no apply. One test checks the default port (`https://api.example.internal:8443`) and one checks a custom port (`:9443`).
- **go.mod and go.sum:** `test/go.sum` was missing, so no Go test could run, including the existing one. I ran `go mod tidy`, which changed `test/go.mod` and added `test/go.sum`. Please review those two changes.
- **Vet disabled:** a plain `go test` hit "disk quota exceeded" in `/tmp` during the vet step. I ran with `-vet=off` instead, so vet has not checked the tests.
- **Not run:** `tflint`, because it isn't installed here. The integration suite wasn't run either, because it applies and belongs to the platform team.
- **Checks that passed:** `terraform fmt -check` is clean, and no state, plan or `.terraform` files were left in the tree.
