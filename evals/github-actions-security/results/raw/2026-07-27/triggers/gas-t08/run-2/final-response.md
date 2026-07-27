I don't have file-write tools available in this session (only Glob, Grep, Read, and Skill), so I can't edit the Dockerfile directly. Here's the fix to apply — add a non-root user and switch to it before running the app:

```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
RUN useradd --create-home --uid 1000 appuser && chown -R appuser:appuser /app
USER appuser
CMD ["python", "-m", "app"]
```

This creates an unprivileged `appuser`, gives it ownership of `/app`, and switches to it with `USER appuser` before the container's entrypoint runs. Let me know if you'd like me to try again with write access enabled, or if you'd rather apply this manually.
