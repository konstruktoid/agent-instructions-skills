I don't have a file-write tool available in this session, so I can't apply the fix directly to disk — but here's the corrected `docker-compose.yml` with consistent 2-space indentation (the original mixed 4-space and 6-space indents, which is what broke parsing):

```yaml
services:
  web:
    image: nginx:1.27
    ports:
      - "8080:80"
  db:
    image: postgres:17
```

Changes: `web`/`db` now at 2 spaces under `services`, their keys (`image`, `ports`) at 4 spaces, and the `ports` list item at 6 spaces — all multiples of the same 2-space step, whereas the original jumped between 4 and 6 inconsistently for sibling keys. Let me know if you'd like me to write this back to the file — I'd need you to apply it since I don't have edit access here.
