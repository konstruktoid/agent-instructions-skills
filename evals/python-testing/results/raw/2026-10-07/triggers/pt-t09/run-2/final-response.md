I couldn't create the test file because the Write tool is disabled in this session, and I have no other way to edit files here. Nothing has been written or run.

This is the test I would add as `cmd/parser_test.go`:

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
		{name: "plain text", line: "name=widget", want: "name=widget"},
		{name: "surrounding whitespace is preserved", line: "  name=widget  ", want: "  name=widget  "},
		{name: "comment line", line: "# a comment", want: "# a comment"},
		{name: "unicode", line: "名前=ウィジェット", want: "名前=ウィジェット"},
		{name: "embedded tab", line: "a\tb", want: "a\tb"},
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

- **The parser does nothing yet.** `Parse` in `cmd/parser.go` just returns its input. The cases above only pin down that pass-through behavior. If the parser is going to do real work, such as splitting key/value pairs, trimming whitespace or skipping comments, tell me the intended rules. I'll write cases for those, including error cases.
- **There's no `go.mod`.** `go test ./cmd/...` won't run until the repo has a module. I haven't created one, because I don't know the module path you want.

If you enable file writes, or you paste the test in yourself, I can run it and expand the cases.
