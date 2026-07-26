I don't have a file-editing tool available in this session (only Glob, Grep, Read, and Skill), so I can't apply this change directly. Here's the fix — replace the Dockerfile contents with:

```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
RUN groupadd -r app && useradd -r -g app app && chown -R app:app /app
USER app
CMD ["python", "-m", "app"]
```

This creates a dedicated non-root `app` user/group, gives it ownership of `/app`, and switches to it via `USER app` before the container runs the application.
