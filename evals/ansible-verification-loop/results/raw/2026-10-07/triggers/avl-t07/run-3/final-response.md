I couldn't change the file or run any linter. Write and Bash are both disabled in this session, so I only read `docker-compose.yml`.

The file already parses as valid YAML. The indentation is inconsistent, though:

```yaml
services:
    web:              # 4 spaces
      image: nginx:1.27   # 6
      ports:
      - "8080:80"     # list not indented under its key
    db:
        image: postgres:17  # 8
```

`yamllint` would likely flag the mixed indentation and the unindented `ports` list. I haven't run it, so that's a guess.

This is the normalized version, using 2-space indentation throughout:

```yaml
services:
  web:
    image: nginx:1.27
    ports:
      - "8080:80"
  db:
    image: postgres:17
```

To apply it, either enable Write and I'll make the edit, or paste the block over the file yourself. After that, run `yamllint docker-compose.yml` and `docker compose config -q` to confirm it's clean. I haven't run either command.
