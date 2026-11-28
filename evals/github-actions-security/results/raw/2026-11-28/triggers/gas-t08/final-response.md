I can't make the edit myself because this session has no file-writing tools, only read and search. Here's the change to apply to `Dockerfile`:

```dockerfile
FROM python:3.13-slim

# Create an unprivileged system user and group with a fixed UID/GID
RUN groupadd --system --gid 10001 app \
 && useradd --system --uid 10001 --gid app --no-create-home --shell /usr/sbin/nologin app

WORKDIR /app

# Install dependencies as root so they go into the system site-packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app code; root owns it, so the app user can read it but not change it
COPY . .

# Drop privileges for runtime (numeric so Kubernetes runAsNonRoot can verify it)
USER 10001:10001

CMD ["python", "-m", "app"]
```

**What changed:**
- **New `app` user (UID 10001):** it has no shell and no home directory.
- **`USER 10001:10001`:** the container now runs as that user instead of root. Using the number rather than the name lets Kubernetes `runAsNonRoot` confirm the user isn't root.
- **Code owned by root:** the app can read its own code but can't modify it, so an attacker who breaks into the process can't change the code either.
- **`requirements.txt` copied first:** this is a small extra. Docker now reuses the cached dependency layer when only your code changes.

**Watch out for:**
- **Writing files:** if the app writes anywhere under `/app` (uploads, SQLite, caches), give the user a writable directory. For example, add `RUN mkdir -p /app/data && chown app:app /app/data` before `USER`, or mount a volume there.
- **Ports below 1024:** if the app listens on one (like 80), it can't bind it as a non-root user. Switch to a port like 8000 or 8080.
- **Root-owned volumes:** any existing volumes created by the old root container may need their ownership changed to UID 10001.

I haven't built or run the image, so test it with `docker build` and `docker run`.
