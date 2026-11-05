The endpoint now renders as `https://HOST:PORT`, and a new unit test fails if the format regresses.

- **Fix:** `outputs.tf` now builds the endpoint as `https://${var.host}:${var.port}`. It previously used `/` between host and port.
- **Regression test:** `test/unit/endpoint_test.go` plans the module and checks the `endpoint` output for the default port (`https://api.example.internal:8443`) and a custom port (`https://api.example.internal:9000`).
- **Verification:** `go test ./unit/...` passes with the fix. I put the old `/` back temporarily and `TestEndpoint` failed, then restored the fix.
- **Test environment:** the first run hit a disk quota error while linking, so I ran the tests with `GOTMPDIR=/tmp/gotmp`. I only ran the unit tests, not the integration test.
- **Go module files:** `go mod tidy` modified `test/go.mod` and created `test/go.sum`, because `go.sum` was missing and the tests wouldn't build without it. Both need to be committed.

I haven't committed anything.
