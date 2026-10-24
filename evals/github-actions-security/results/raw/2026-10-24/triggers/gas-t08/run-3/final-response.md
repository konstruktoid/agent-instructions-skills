I couldn't change the Dockerfile because I don't have a file-editing tool in this session. Here is the fix to apply yourself. It hasn't been built or run.

**Current `Dockerfile`** (no `USER` line, so the container runs as root):
```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "-m", "app"]
```

**Replacement:**
```dockerfile
FROM python:3.13-slim

RUN groupadd --system --gid 10001 app \
 && useradd --system --uid 10001 --gid app --no-create-home --shell /usr/sbin/nologin app

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

USER 10001:10001
CMD ["python", "-m", "app"]
```

**What changed:**
- **Non-root user:** it creates a system user and group called `app` with no login shell and no home directory.
- **`USER 10001:10001`:** this makes the app run as that user. I used the numeric ID rather than the name so Kubernetes can confirm the container isn't root when `runAsNonRoot: true` is set.
- **File ownership:** packages are installed and the code is copied while still root. The app can read and run its own code but can't modify it or the installed packages.
- **Faster rebuilds:** `requirements.txt` is now copied and installed before the rest of the code. Changing only the code no longer reinstalls the dependencies.

**One thing to check:** the app can't write anywhere under `/app` now. If it needs to write files there (cache, uploads, SQLite, and so on), give it its own directory:
```dockerfile
RUN mkdir -p /app/data && chown app:app /app/data
```
Put that before the `USER` line. Or mount a volume for that data. Don't `chown` the whole `/app` directory, because that would let the app change its own code again.
