I can't apply this myself. This session gives me read-only tools (Glob, Grep, Read) and no way to edit or write files, so I couldn't change the `Dockerfile`. Here's the change to make:

```dockerfile
FROM python:3.13-slim

# Create an unprivileged system user and group with a fixed UID/GID
RUN groupadd --system --gid 10001 app \
 && useradd --system --uid 10001 --gid app --no-create-home --shell /usr/sbin/nologin app

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Files stay owned by root and are only readable by the app user, which can't change them
COPY . .

USER 10001:10001

CMD ["python", "-m", "app"]
```

What changed:
- **`USER 10001:10001`**: the container now runs as a dedicated user that can't log in, not as root. Using numeric IDs lets Kubernetes `runAsNonRoot` confirm the user isn't root.
- **Packages are still installed as root**: `pip install` runs before the `USER` switch, so packages go into the system site-packages and the app user can't modify them.
- **Files aren't given to the app user**: I left out `--chown`, so the code stays owned by root and a compromised process can't rewrite it. If the app needs to write somewhere (for example a cache or uploads folder), make just that folder writable before `USER`. For example: `RUN mkdir /app/data && chown app:app /app/data`.
- **Better build caching**: copying `requirements.txt` on its own first means dependencies aren't reinstalled every time the code changes.

Two things to check, since I couldn't build or run it:
- If the app listens on a port below 1024, it won't be able to bind it as a non-root user. Move it to a higher port such as 8000 or 8080.
- Rebuild and start the container to confirm the app still works under the new user.
