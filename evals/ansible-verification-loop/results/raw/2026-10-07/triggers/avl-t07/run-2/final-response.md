I couldn't fix the indentation because the Write tool is disabled in this session, so `docker-compose.yml` is unchanged. I also didn't run a linter. I only read the file, and the shell wasn't used.

The file is already valid YAML, so the current indentation shouldn't break parsing. It's just inconsistent:
- `web` and `db` sit at 4 spaces, but their keys are at 6 and 8 spaces.
- The `ports` list item sits at the same indent as `ports:` itself.

This is the normalized 2-space version I would have written:

```yaml
services:
  web:
    image: nginx:1.27
    ports:
      - "8080:80"
  db:
    image: postgres:17
```

If you enable file writing, I'll apply it and run `docker compose config -q` or `yamllint` to confirm. You can also paste the block above over the file yourself.
