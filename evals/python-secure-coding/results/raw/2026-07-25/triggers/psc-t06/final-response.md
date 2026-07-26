There's no HTTP handler or query-building code in this repo — `cmd/parser.go` is the only Go file, and it's a trivial one-line passthrough with no SQL, no HTTP handling, and no database access at all:

```go
package cmd

func Parse(line string) string {
	return line
}
```

I can't review something that isn't there. Could you point me to the actual file with the HTTP handler and query logic, or paste the code directly?
