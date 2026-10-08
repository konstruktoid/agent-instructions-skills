I couldn't fix the file. The Write tool is disabled in this session, so `docker-compose.yml` is unchanged. I also had no way to run a linter or parser here, so none of this was run. It comes from reading the file.

The file is probably already valid YAML, because each block is indented consistently within itself. It does mix indent widths:

- `web` is indented 4 spaces and its keys 6.
- `db` is indented 4 spaces but its keys 8.
- The `ports` list items sit at the same level as `ports:`.

A linter such as yamllint would flag that, even though a parser accepts it. Here is the version with consistent 2-space indentation:

```yaml
services:
  web:
    image: nginx:1.27
    ports:
      - "8080:80"
  db:
    image: postgres:17
```

If you enable file writes, I can apply it and check it with `docker compose config` or `yamllint`. You can also paste the block above into the file yourself.
