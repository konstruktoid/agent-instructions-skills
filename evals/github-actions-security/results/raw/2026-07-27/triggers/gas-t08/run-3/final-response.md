I don't have a file-editing tool available in this session (only Glob, Grep, Read, and Skill), so I can't apply the change directly. Here's the fix — add a non-root user and switch to it before running the app:

```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt \
    && useradd --no-create-home --shell /usr/sbin/nologin appuser \
    && chown -R appuser:appuser /app
USER appuser
CMD ["python", "-m", "app"]
```

This creates an unprivileged `appuser`, gives it ownership of `/app`, and switches to it via `USER` before the container's entrypoint runs. If you can grant Edit/Write tool access, I'll apply this directly instead of just showing it.
