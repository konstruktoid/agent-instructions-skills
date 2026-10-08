I couldn't write `cmd/parser_test.go` because the Write tool is disabled in this session. Here is the test so you can save it yourself, or re-enable Write and I'll create it.

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
		{name: "simple line", line: "name=foo", want: "name=foo"},
		{name: "surrounding whitespace is preserved", line: "  name=foo  ", want: "  name=foo  "},
		{name: "comment line", line: "# comment", want: "# comment"},
		{name: "unicode", line: "名前=値", want: "名前=値"},
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

- **Current behavior:** `Parse` in `cmd/parser.go` returns its input unchanged, so every case expects the input back. These cases pin that identity behavior. When `Parse` starts trimming, skipping comments or validating, update the `want` values and add error cases.
- **Not run:** I haven't run the test. The repo has no `go.mod`, so `go test ./cmd/` won't work until you run `go mod init <module>`.
