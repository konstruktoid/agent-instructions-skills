The endpoint now renders as `https://HOST:PORT`. I changed `outputs.tf` to use `${var.host}:${var.port}` instead of `${var.host}/${var.port}`.

To stop it regressing, I added `TestEndpointFormat` to `test/unit/service_name_test.go`. It plans with host `api.example.internal` and port 8443 and asserts the endpoint is exactly `https://api.example.internal:8443`. I ran `go test ./unit/...` and it passes, but I didn't run it against the old `/` version, so I haven't seen it fail on the bug.

`go mod tidy` also updated `test/go.mod` and `test/go.sum`, because the tests wouldn't build without the missing `go.sum` entries. I didn't run the integration test, which needs a real apply.

I haven't committed anything.
