The endpoint now renders as `https://HOST:PORT`, and a new test guards it against regressing.

- **Fix:** in `outputs.tf`, `endpoint` now uses `"https://${var.host}:${var.port}"`.
- **Test:** I added `test/unit/endpoint_test.go`, which follows the existing one-file-per-output convention. It plans without applying and checks the default port (`https://api.example.internal:8443`) and an explicit port (`...:9000`).
- **Results:** with the old `/` in place, the test failed on both cases (`https://api.example.internal/9000` instead of `:9000`). With the fix, `go test ./unit/...` passes. `terraform fmt -check` is clean.
- **`go.sum`:** it was missing, so no test in `test/` could build, including the existing one. I ran `go mod tidy`, which added `test/go.sum` and filled in the indirect requirements in `test/go.mod`. Both need committing.
- **Not run:** I didn't run `tflint`, and I didn't run the integration tests, which apply infrastructure and are the platform team's.

I haven't committed anything.
