I can't make the change myself. This session only gives me tools to read and search files, with no way to edit or write them. Here's the updated `Dockerfile` for you to apply:

```dockerfile
FROM python:3.13-slim

# Create an unprivileged system user and group with fixed IDs
RUN groupadd --system --gid 10001 app \
 && useradd --system --uid 10001 --gid app --no-create-home --shell /usr/sbin/nologin app

WORKDIR /app

# Install dependencies as root, so the installed packages stay owned by root
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code; it stays owned by root, so the app user can read it but not change it
COPY . .

# Everything from here on, including the app at runtime, runs as the unprivileged user
USER 10001:10001

CMD ["python", "-m", "app"]
```

**What changed:**
- **A dedicated unprivileged user:** it has fixed IDs and can't be used to log in. Fixed IDs make file ownership on mounted volumes predictable.
- **`USER 10001:10001`:** the app now runs as that user instead of root. Giving the number rather than the name also lets Kubernetes `runAsNonRoot` confirm the container isn't root.
- **The code stays owned by root:** I didn't add `--chown` to the copy. The app can read its code but can't change it, which limits the damage if it's compromised.
- **Dependencies are copied first:** `requirements.txt` is now copied before the rest of the code, so Docker can reuse the installed packages when only your code changes. This is a speed-up, not a security fix.

**Check after applying:**
- If the app writes anything to disk (logs, uploads, cache), it will now fail with a permission error. Create those folders and give them to the app user, for example `RUN mkdir /app/data && chown app:app /app/data` before the `USER` line, or mount a volume there.
- If the app listens on a port below 1024, switch it to one above 1024 (e.g. 8080). Users other than root can't open those low ports by default.
- To confirm it worked: `docker run --rm <image> id` should show `uid=10001`.
