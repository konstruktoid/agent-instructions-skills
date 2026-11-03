I don't have a file-writing tool in this session, so the test is below for you to save as `cmd/parser_test.go`. I haven't run it.

Right now `Parse` (`cmd/parser.go:4`) just returns its input unchanged. The doc comment says it "turns a manifest line into a record," but no record format exists yet, so this test only checks the current pass-through behavior. That includes edge cases like empty input, whitespace, comments and Unicode, so any later change to how those are handled will show up as a failing test.

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
		{name: "simple key=value", line: "name=widget", want: "name=widget"},
		{name: "preserves leading and trailing whitespace", line: "  name=widget  ", want: "  name=widget  "},
		{name: "preserves tabs", line: "name\twidget", want: "name\twidget"},
		{name: "comment line", line: "# a comment", want: "# a comment"},
		{name: "unicode", line: "név=ütköző", want: "név=ütköző"},
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

**Before you run it:**
- **No `go.mod`:** the repo doesn't have one, so `go test ./cmd/...` won't work until you create it (for example, `go mod init <module-path>`).
- **Updating the test later:** when `Parse` starts returning a real record type, change the `want` field's type to match. Then add cases for malformed lines, and an `wantErr bool` field if the function ends up returning an error.
