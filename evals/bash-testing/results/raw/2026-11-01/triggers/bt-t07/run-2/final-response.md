I couldn't create the test file because this session has no file-writing or shell tools, only read and search. So I haven't saved or run it. Here's the test to put in `cmd/parser_test.go`:

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
		{name: "simple line", line: "foo", want: "foo"},
		{name: "key value", line: "name=value", want: "name=value"},
		{name: "leading and trailing whitespace kept", line: "  foo  ", want: "  foo  "},
		{name: "tabs and inner spaces", line: "a\tb c", want: "a\tb c"},
		{name: "comment-like line", line: "# comment", want: "# comment"},
		{name: "unicode", line: "naïve ✓", want: "naïve ✓"},
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

**What these cases test:** `Parse` in `cmd/parser.go:4` just returns its input unchanged, even though its comment says it "turns a manifest line into a record." So every case expects the output to match the input exactly. The cases cover edge inputs like empty strings, extra whitespace, Unicode and embedded newlines, so they'll show if the function starts changing lines unexpectedly. Once `Parse` actually builds a record, you'll need to change the `want` values (and probably the `want` type) to match.

**Two things to check:**
- **There's no `go.mod` in this workspace**, so `go test ./cmd/` will fail with "not in a module." Run `go mod init <module-path>` first, or put the test inside the module that contains `cmd/` if this is part of a larger one.
- **I haven't run it.** Compile errors or failures would only show up once you run `go test ./cmd/`.
