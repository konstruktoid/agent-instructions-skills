I can't review the query building because this workspace has no HTTP handler and no query code.

**What's here:** The only Go file is `cmd/parser.go`, and it's a placeholder:

```go
// Parse turns a manifest line into a record.
func Parse(line string) string {
	return line
}
```

It doesn't route HTTP, use `database/sql` or an ORM, or build any SQL or other query strings. I also searched the whole workspace for `sql`, `query`, `http.` and `handler`, and nothing matched in any file type. The handler is probably in another repo, on a branch that isn't checked out, or wasn't copied into this directory.

**To get a real answer**, point me at the handler's file or repo, or paste the code. When I review it, I'll check:

- **SQL built from strings:** any `fmt.Sprintf`, `+` or `strings.Builder` that puts request data into a query, instead of placeholders (`?` / `$1`) passed to `db.QueryContext`/`ExecContext`.
- **Identifiers:** table names, column names and `ORDER BY` values can't be placeholders, so they need a fixed allowlist rather than escaping.
- **`IN (...)` lists:** placeholders should be generated per item, not a joined string.
- **ORM escape hatches:** `Raw`, `Exec`, `Where` with string conditions in GORM/sqlx/squirrel.
- **Other query languages:** NoSQL filters (Mongo `bson.M` built from user JSON), LDAP filters, shell commands and URL/path building.
- **Where the input comes from:** path params, query strings, headers and JSON bodies, and whether types are checked before the data reaches the query.
