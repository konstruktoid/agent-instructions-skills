I couldn't save a file this session because I only have read and search tools, no write or shell tools. So I haven't created or run the test. Here's what it should look like, based on the actual parser.

**What `Parse` does now** (`cmd/parser.go:4`): it returns the input line unchanged. The comment says it turns a manifest line into a record, but no parsing happens yet. A table-driven test can only check that the input comes back as-is. These cases fix today's behaviour so you'll notice when real parsing lands, and you'll need to update the expected values then.

Proposed `cmd/parser_test.go`:

```go
package cmd

import "testing"

func TestParse(t *testing.T) {
	tests := []struct {
		name string
		line string
		want string
	}{
		{name: "empty line", line: "", want: ""},
		{name: "simple line", line: "name=value", want: "name=value"},
		{name: "leading and trailing whitespace preserved", line: "  key = val  ", want: "  key = val  "},
		{name: "comment line", line: "# a comment", want: "# a comment"},
		{name: "unicode", line: "név=érték", want: "név=érték"},
		{name: "embedded newline", line: "a\nb", want: "a\nb"},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := Parse(tt.line); got != tt.want {
				t.Errorf("Parse(%q) = %q, want %q", tt.line, got, tt.want)
			}
		})
	}
}
```

**Before it will run:**
- **There's no `go.mod`** in the workspace, so `go test ./cmd/` will fail in module mode. Run `go mod init <module-path>` at the repo root first, then `go test ./cmd/ -v`.
- **This repo is mostly Python** (`src/ledger/`, `tests/test_balance.py`), and `cmd/parser.go` is the only Go file. If the Go parser is supposed to live elsewhere, tell me where and I'll base the tests on that code instead.
- **What's a manifest line?** If you can describe the record format (fields, separators, what should be rejected), I'll change the table to test the real parsing, including error cases. `Parse` doesn't return an error yet, so error cases would also need a signature change, such as `(Record, error)`.

If you turn on write and shell access, I can add the file and run the tests myself.
