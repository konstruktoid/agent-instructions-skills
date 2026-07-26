This session's tool set only gives me Glob/Grep/Read/Skill — no file-write or shell-execution tools, so I can't create the test file or run `go test` myself. Here's the table-driven test for `cmd/parser.go` to add as `cmd/parser_test.go`:

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
		{"line with whitespace", "  hello  ", "  hello  "},
		{"line with special characters", "key=value;flag", "key=value;flag"},
		{"multiline input", "line1\nline2", "line1\nline2"},
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

Note: there's no `go.mod` in this directory, so `go test ./...` won't run until one exists (e.g. `go mod init <module>`). Let me know if you'd like me to create the file and `go.mod` — I'll need you to run the write/execute, or grant me a tool that can.
