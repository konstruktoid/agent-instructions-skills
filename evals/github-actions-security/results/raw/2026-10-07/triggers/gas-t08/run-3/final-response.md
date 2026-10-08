I couldn't change the Dockerfile. `Write` is disabled in this session, and I have no other file-editing tool, so the file is unchanged.

The current `Dockerfile` runs as root because it never sets a `USER`. This version fixes that:

```dockerfile
FROM python:3.13-slim
RUN groupadd --system --gid 10001 app \
    && useradd --system --uid 10001 --gid app --no-create-home --shell /usr/sbin/nologin app
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY --chown=app:app . .
USER app
CMD ["python", "-m", "app"]
```

- **Non-root user:** it creates a system user and group with a fixed UID/GID of 10001, no home directory and no login shell. `USER app` is set after the install step, so `pip` still runs as root and the app does not.
- **Layer caching:** `requirements.txt` is copied and installed before the rest of the source. Code changes no longer invalidate the dependency layer.
- **File ownership:** `COPY --chown=app:app` makes the app files owned by the unprivileged user.

I haven't built or run this. If the app writes to a path outside `/app`, such as a data or log directory, that path will need to be created and `chown`ed to `app` as well.

If you allow file edits, or paste this in yourself, I can apply it and run a build to check it.
