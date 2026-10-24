I haven't changed the Dockerfile because I can only read and search files here, not write them. Here's the fix to paste in.

**Current `Dockerfile`:**
```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "-m", "app"]
```

No `USER` is set, so the app runs as root.

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

What changed:
- **A dedicated system user (`app`, UID/GID 10001)** with no home directory and no login shell.
- **`USER 10001:10001` comes after the install steps.** Packages still install system-wide as root, but the app itself runs unprivileged. Using the numeric ID lets Kubernetes `runAsNonRoot` confirm it's not root.
- **The app's files stay owned by root.** I didn't use `COPY --chown`, so the app user can read its code but can't change it at runtime. If the app needs to write somewhere, add a specific directory for that, e.g. `RUN mkdir /app/data && chown app:app /app/data`.
- **`requirements.txt` is copied first, separately.** This isn't part of the root fix, but code changes no longer force the dependency layer to rebuild.

Things to check:
- If the app listens on a port below 1024 (e.g. 80), it won't be able to bind it as non-root. Move it to a higher port like 8000 or 8080.
- A `.dockerignore` file excluding `.git`, `.env` and similar would stop `COPY . .` from putting secrets in the image. I didn't look for one.

I haven't built or run this image. Once you've applied it, `docker run --rm <image> id` should report `uid=10001`.
