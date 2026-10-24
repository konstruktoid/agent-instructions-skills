I can't apply the fix myself: this session has no file-editing or shell tool, only read and search. Here's the change to make in `Dockerfile`.

**Current file (`Dockerfile:1-5`):** there's no `USER` instruction, so `python -m app` runs as root (UID 0).

**Replacement:**

```dockerfile
FROM python:3.13-slim

# Create an unprivileged system user and group with a fixed UID/GID and no login shell
RUN groupadd --system --gid 10001 app \
 && useradd --system --uid 10001 --gid app --no-create-home --shell /usr/sbin/nologin app

WORKDIR /app

# Install dependencies as root so the app user can't change installed packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Source stays owned by root, so the app can read it but not change it
COPY . .

USER 10001:10001
CMD ["python", "-m", "app"]
```

**What changes:**
- **Dedicated user:** adds `app` (UID/GID 10001) with no login shell or home directory.
- **Numeric `USER 10001:10001`:** Kubernetes `runAsNonRoot` can only confirm a numeric UID isn't root, so this passes that check.
- **Read-only code and dependencies:** the code and installed packages stay owned by root. If the app is compromised, it can't change its own code or dependencies.
- **Better build caching:** copying `requirements.txt` before the rest of the source means the dependency layer is only rebuilt when requirements change.

**Check these when you apply it:**
- **Writable paths:** if the app writes to disk (uploads, a SQLite file, logs under `/app`), create those directories and give them to the app user, e.g. `RUN mkdir /app/data && chown app:app /app/data` before `USER`. A mounted volume works too.
- **Ports below 1024:** a non-root user can't bind to them. If the app listens on port 80 or similar, switch to a higher port like 8000 or 8080.
- **`.dockerignore`:** `COPY . .` copies the whole build context. Make sure `.git`, `.env` and other secrets are listed in `.dockerignore`.

None of this has been built or run. After applying it, `docker build -t app . && docker run --rm app id` should show `uid=10001`. Then run the app normally to catch any permission errors on paths it writes to.
