I couldn't change the Dockerfile. The Write tool is disabled in this session, and I have no other tool that edits files. The file is untouched.

This is the fix I would have made to `Dockerfile`:

```dockerfile
FROM python:3.13-slim
RUN groupadd --system --gid 10001 app \
    && useradd --system --uid 10001 --gid app --no-create-home --shell /usr/sbin/nologin app
WORKDIR /app
COPY --chown=app:app . .
RUN pip install --no-cache-dir -r requirements.txt
USER app
CMD ["python", "-m", "app"]
```

- **Unprivileged user:** it creates a system user and group with a fixed UID and GID of 10001. A fixed ID works with Kubernetes `runAsNonRoot` checks and with volume permissions.
- **Install as root:** `pip install` still runs as root, before the `USER app` line, so packages go into the system site-packages. The app can't modify them at runtime.
- **App files:** `COPY --chown=app:app` makes the app files owned by the new user. Without it they would stay root-owned and read-only to the app.
- **Runtime user:** `USER app` comes just before `CMD`, so the app runs without root.

I haven't built the image or run it. If the app writes to disk at runtime, for example to `/app` or a cache directory, that path will need to be writable by `app`.

Re-enable file editing and I'll apply the change. You can also paste the block above in yourself.
