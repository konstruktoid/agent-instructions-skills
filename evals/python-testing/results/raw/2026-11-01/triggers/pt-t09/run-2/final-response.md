I don't have file-writing or shell tools in this session, so I couldn't create or run the test. Here's the file to add as `cmd/parser_test.go`.

There isn't much to test yet. `Parse` at `cmd/parser.go:4` returns its input unchanged, even though its comment says it turns a manifest line into a record. These tests lock in that current pass-through behaviour.

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
		{name: "simple token", line: "foo", want: "foo"},
		{name: "key value", line: "name=value", want: "name=value"},
		{name: "surrounding whitespace preserved", line: "  foo  ", want: "  foo  "},
		{name: "internal tabs preserved", line: "a\tb", want: "a\tb"},
		{name: "trailing newline preserved", line: "foo\n", want: "foo\n"},
		{name: "comment-like line", line: "# comment", want: "# comment"},
		{name: "unicode", line: "nämn=värde", want: "nämn=värde"},
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

**Before you run it:**
- **No `go.mod`:** the workspace doesn't have one, so `go test` will fail. Run `go mod init <module-path>` at the repo root first, then `go test ./cmd/...`.
- **Expectations may need to change:** the whitespace, newline and comment cases only check that the input comes back unchanged. When `Parse` starts producing real records, its return type will probably change from `string` to a struct, and those expectations will need updating. If you tell me what a manifest line looks like and what record it should become, I can write tests for that behaviour instead.
