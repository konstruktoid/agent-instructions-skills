I can't save this to disk because my tools here can only read and search files, not write them. Here is the file to save as `cmd/parser_test.go`:

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
		{name: "simple key=value", line: "name=nginx", want: "name=nginx"},
		{name: "leading and trailing whitespace kept", line: "  image: nginx:1.27  ", want: "  image: nginx:1.27  "},
		{name: "embedded tab", line: "replicas\t3", want: "replicas\t3"},
		{name: "comment line", line: "# managed by ansible", want: "# managed by ansible"},
		{name: "unicode", line: "owner=thosjö", want: "owner=thosjö"},
		{name: "trailing newline kept", line: "port=8080\n", want: "port=8080\n"},
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

A few things to know:

- **What it tests:** `Parse` (`cmd/parser.go:4`) currently returns its input unchanged, even though its comment says it "turns a manifest line into a record". So each test case expects exactly its input back. The cases cover the edge cases a real parser will have to decide on: empty lines, whitespace, tabs, comments, Unicode and trailing newlines. When `Parse` starts doing real work, update the `want` values and add cases for invalid input.
- **No `go.mod`:** The workspace has no `go.mod`, so `go test ./cmd/...` won't run yet. Run `go mod init <module-path>` at the repo root first.
- **Not run:** I haven't compiled or run this test because I can't run commands here. After saving it, run `go test ./cmd/ -run TestParse -v`.
