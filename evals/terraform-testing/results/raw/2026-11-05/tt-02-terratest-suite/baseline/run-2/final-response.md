The endpoint now renders as `https://HOST:PORT`. I fixed it in `outputs.tf` by changing the `/` before the port to `:`.

To keep it from regressing, I added two plan-based tests to `test/unit/service_name_test.go`. One checks a custom port (`https://api.example.internal:9443`) and one checks the default (`https://api.example.internal:8443`). `go test ./unit/` passes. I didn't run the tests against the old code, so I haven't seen them fail on the bug.

`go mod tidy` created or updated `test/go.sum`, which was missing and stopped the tests from building. I left it uncommitted. The integration test under `test/integration` was not run.
