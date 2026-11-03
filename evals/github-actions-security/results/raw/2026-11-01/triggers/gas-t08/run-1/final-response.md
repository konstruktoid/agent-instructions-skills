I couldn't change the file because I only have read and search tools in this session. Here is the change to make to `Dockerfile`:

```dockerfile
FROM python:3.13-slim

# Unprivileged system user and group with a fixed UID/GID and no login shell
RUN groupadd --system --gid 10001 app \
 && useradd --system --uid 10001 --gid app --no-create-home --shell /usr/sbin/nologin app

WORKDIR /app

# Install dependencies as root, so the app user can't modify site-packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code stays owned by root, so the app user can read it but not change it
COPY . .

USER 10001:10001
CMD ["python", "-m", "app"]
```

What changed and why:

- **`USER 10001:10001`**: this is the actual fix. The `CMD` now runs as an unprivileged user instead of root. I used the number rather than the name so Kubernetes `runAsNonRoot` can confirm the user isn't root without looking it up.
- **Fixed UID/GID and no shell**: the IDs stay the same across rebuilds, which keeps volume permissions predictable. The account can't be used to log in.
- **Code stays owned by root**: I deliberately didn't use `COPY --chown=app`. If someone gets control of the process, they can't rewrite its code or installed packages.
- **`requirements.txt` copied first**: not needed for security, but the pip layer now stays cached when only the code changes.

Things to check:

- If the app writes to a path under `/app` at runtime (cache, uploads, SQLite file), add `RUN mkdir -p /app/data && chown 10001:10001 /app/data` before `USER`, or mount a volume there.
- If the app binds to a port below 1024 (for example 80), it will now fail as non-root. Switch it to a higher port such as 8000 or 8080.

I haven't built or run this image.
