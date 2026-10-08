I couldn't create `cmd/parser_test.go`. The Write tool is disabled in this session, and I have no other way to create files. Here is the test so you can save it yourself:

```go
package cmd

import "testing"

func TestParse(t *testing.T) {
	tests := []struct {
		name string
		in   string
		want string
	}{
		{name: "empty", in: "", want: ""},
		{name: "simple", in: "name=value", want: "name=value"},
		{name: "leading and trailing space", in: "  name=value  ", want: "  name=value  "},
		{name: "tabs", in: "a\tb", want: "a\tb"},
		{name: "unicode", in: "名前=値", want: "名前=値"},
		{name: "comment", in: "# comment", want: "# comment"},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := Parse(tt.in); got != tt.want {
				t.Errorf("Parse(%q) = %q, want %q", tt.in, got, tt.want)
			}
		})
	}
}
```

I haven't run it, because I couldn't create the file and had no way to run `go test`.

- **Stub parser:** `Parse` currently returns its input unchanged, so these cases only pin that identity behavior. When real parsing is added, update the `want` values and add cases for malformed input and any error returns.
- **No `go.mod`:** I found no `go.mod` in the workspace, so you'll need to run `go mod init <module>` before `go test ./cmd/...` will work.

If you enable Write, or tell me another way to save the file, I'll add it and run the tests.
