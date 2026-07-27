I don't have file-editing tools available in this session (only search/read tools), so I can't apply the change directly. Here's the fix you can apply to `Dockerfile`:

```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
RUN groupadd -r app && useradd -r -g app app && chown -R app:app /app
USER app
CMD ["python", "-m", "app"]
```

This creates a dedicated non-root user/group, gives it ownership of `/app`, and switches to it with `USER app` before the container runs. Let me know if you'd like me to make another attempt with editing tools enabled, or if you'd like to apply this yourself.
