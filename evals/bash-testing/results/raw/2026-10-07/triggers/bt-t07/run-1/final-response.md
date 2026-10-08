I couldn't create `cmd/parser_test.go` because the Write tool is disabled in this session. I haven't run the test either. There's also no `go.mod` in the workspace, so `go test` would need one first.

`Parse` currently just returns its input unchanged. The test below pins that behavior, so you'll need to change the cases if `Parse` gains real logic. Here is the file to save as `cmd/parser_test.go`:

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
		{name: "single token", line: "alpha", want: "alpha"},
		{name: "key value", line: "name=widget", want: "name=widget"},
		{name: "leading and trailing spaces", line: "  padded  ", want: "  padded  "},
		{name: "tabs", line: "a\tb", want: "a\tb"},
		{name: "comment line", line: "# comment", want: "# comment"},
		{name: "unicode", line: "naïve-日本語", want: "naïve-日本語"},
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

If you re-enable Write, I can save it and run `go test ./cmd/...`.
