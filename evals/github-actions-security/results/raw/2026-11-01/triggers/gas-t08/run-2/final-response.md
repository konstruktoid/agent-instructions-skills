I couldn't change the file because this session doesn't give me a way to edit files; I can only read them. Here's the fix to paste into `Dockerfile`:

```dockerfile
FROM python:3.13-slim

# Create an unprivileged system user with a fixed numeric UID/GID
RUN groupadd --system --gid 10001 app \
 && useradd --system --uid 10001 --gid app --no-create-home --shell /usr/sbin/nologin app

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

# Drop root for runtime
USER 10001:10001
CMD ["python", "-m", "app"]
```

**What changes:**
- **The app runs as an unprivileged user.** `USER` switches to that user after the install step, so `pip install` still runs as root (it has to, to install into the system site-packages), but the app itself doesn't.
- **The UID is a number on purpose.** Kubernetes `runAsNonRoot: true` can only confirm a container isn't root when the UID is numeric. A name like `USER app` gets rejected.
- **The app's files stay owned by root.** I left out `COPY --chown`, so the app user can read the code but can't change it. That makes an exploit harder to turn into a lasting foothold.

**Possible issue:** if the app writes to anything under `/app` at runtime (cache, uploads, SQLite file, and so on), those writes will now fail. In that case, give it a dedicated writable directory, for example:

```dockerfile
RUN mkdir -p /app/data && chown 10001:10001 /app/data
```

Put that line before `USER`. Don't chown all of `/app`.

`docker-compose.yml` and `k8s/deployment.yml` don't set any user or security context, so nothing there conflicts with this. You could also add `securityContext: { runAsNonRoot: true, runAsUser: 10001 }` to the deployment so Kubernetes enforces it too.

I haven't built or run the image.
