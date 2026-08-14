I don't have a file-write tool available in this session, so I can't create `cmd/parser_test.go` directly — here's the table-driven test to add to the repo:

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
		{name: "simple line", line: "id=1,name=foo", want: "id=1,name=foo"},
		{name: "line with spaces", line: "  padded  ", want: "  padded  "},
		{name: "line with unicode", line: "héllo wörld", want: "héllo wörld"},
		{name: "line with embedded newline", line: "first\nsecond", want: "first\nsecond"},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := Parse(tt.line)
			if got != tt.want {
				t.Errorf("Parse(%q) = %q, want %q", tt.line, got, tt.want)
			}
		})
	}
}
```

Note: `Parse` in `cmd/parser.go` currently just returns its input unchanged (an identity stub), so every case necessarily passes — the tests mainly pin current behavior so a regression is caught once real parsing logic is added. Also, there's no `go.mod` in this workspace, so `go test ./...` won't run as-is; let me know if you'd like me to check for that or if it lives elsewhere in the repo.
