I don't have write access in this session, so I can't create the file directly. Here's the table-driven test to add as `cmd/parser_test.go`:

```go
package cmd

import "testing"

func TestParse(t *testing.T) {
	tests := []struct {
		name string
		line string
		want string
	}{
		{
			name: "empty line",
			line: "",
			want: "",
		},
		{
			name: "simple line",
			line: "record1",
			want: "record1",
		},
		{
			name: "line with whitespace",
			line: "  record with spaces  ",
			want: "  record with spaces  ",
		},
		{
			name: "line with delimiters",
			line: "field1,field2,field3",
			want: "field1,field2,field3",
		},
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

Note: `cmd/parser.go` currently just echoes the input line back unchanged, so the test covers that identity behavior across a few representative inputs (empty, plain, whitespace-padded, delimited). There's no `go.mod` in this repo yet, so `go test` won't run until one is added — let me know if you'd like me to set that up too.
