The Write tool is disabled in this session, so I can't create the test file directly. Here's the table-driven test to add as `cmd/parser_test.go`:

```go
package cmd

import "testing"

func TestParse(t *testing.T) {
	tests := []struct {
		name string
		line string
		want string
	}{
		{"empty line", "", ""},
		{"simple line", "hello", "hello"},
		{"line with whitespace", "  hello world  ", "  hello world  "},
		{"line with special characters", "key=value;other=1", "key=value;other=1"},
		{"line with unicode", "héllo wörld 日本語", "héllo wörld 日本語"},
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

Note: `Parse` currently just returns its input unchanged (`cmd/parser.go:5`), so these cases mostly pin down identity behavior — once real parsing logic lands, update `want` accordingly. There's no `go.mod` in this repo, so I couldn't run `go test` to verify; you'll want to confirm it compiles/passes once the module is set up.
