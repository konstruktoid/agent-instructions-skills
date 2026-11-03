I couldn't create the file because I only have read and search tools in this session. Below is the test file to drop in. I also haven't run it.

**What the parser does now** (`cmd/parser.go:4`): `Parse` returns its input unchanged. It's a stub, so the only behavior a test can check today is that the input comes back as-is. The table is set up so you can update the `want` values and add cases once the real record format exists.

`cmd/parser_test.go`:

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
		{name: "simple token", line: "foo", want: "foo"},
		{name: "key value", line: "name=widget", want: "name=widget"},
		{name: "surrounding whitespace preserved", line: "  foo  ", want: "  foo  "},
		{name: "internal tabs", line: "a\tb\tc", want: "a\tb\tc"},
		{name: "comment line", line: "# comment", want: "# comment"},
		{name: "unicode", line: "naïve-π", want: "naïve-π"},
		{name: "trailing newline", line: "foo\n", want: "foo\n"},
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

**Before it will run:**
- **No `go.mod`:** the repo doesn't have one, so `go test` won't work yet. Run `go mod init <module-path>` at the repo root, then `go test ./cmd/...`.
- **Rows that will need updating:** the whitespace, comment and trailing-newline rows check that the input passes through untouched. Once `Parse` really parses, you'll probably want those lines trimmed, skipped or rejected, so change those `want` values.
- **Errors:** if `Parse` ends up returning a struct or an `error`, change `want` to that type and add a `wantErr bool` field. Then use `reflect.DeepEqual` or `cmp.Diff` to compare.

If you tell me the manifest line format, I can write rows that test the real parsing rules.
