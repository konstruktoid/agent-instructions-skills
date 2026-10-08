I couldn't create the test file because the Write tool is disabled in this session. I haven't run anything either, since there's no `go.mod` in the workspace. Here is the file I meant to add as `cmd/parser_test.go`:

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
		{name: "surrounding whitespace is preserved", line: "  name=value  ", want: "  name=value  "},
		{name: "comment line", line: "# a comment", want: "# a comment"},
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

- **Placeholder parser:** `Parse` in `cmd/parser.go` currently just returns its input, and its comment says it turns a manifest line into a record. The cases above only lock in that pass-through behavior. Once the real parsing exists, the table needs real inputs, expected records, and error cases.
- **Missing module file:** the workspace has no `go.mod`, so `go test ./...` won't work until you run `go mod init <module path>`. I haven't created one because I don't know your module path.
- **Skill choice:** I didn't use the `python-testing` skill because this is a Go package.

If you enable Write, I'll add the file and run `go test ./cmd/...`. If you can describe the manifest line format, I'll replace the placeholder cases with real ones.
