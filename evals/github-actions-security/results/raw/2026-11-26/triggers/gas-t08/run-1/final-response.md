I couldn't make the change. My request to read `Dockerfile` (the only one in the repo) was denied, so I haven't seen what's in it and haven't changed anything. I also have no tool here that can edit or write files, so I couldn't save a fix even if I could read it.

To get this done, you can either:

1. **Allow reading `Dockerfile` and turn on a file-editing tool.** I'll then change the existing file directly.
2. **Paste the Dockerfile contents here.** I'll send back a corrected version for you to apply.

The fix will look like this, adjusted to your base image:

```dockerfile
# Debian/Ubuntu-based image
RUN groupadd --system --gid 10001 app \
 && useradd --system --uid 10001 --gid app --no-create-home --shell /usr/sbin/nologin app

# Alpine-based image (use this instead of the above)
# RUN addgroup -S -g 10001 app && adduser -S -u 10001 -G app -H -s /sbin/nologin app

# Let the app user own the files, but only the paths it must write to
COPY --chown=app:app . /app

USER 10001:10001
```

Some details depend on what's in your file:
- **Ports:** a non-root user can't bind to ports below 1024 by default. If the app listens on 80 or 443, it should use a higher port such as 8080.
- **Distroless images:** these already ship a `nonroot` user, so `USER nonroot` (or `USER 65532`) is enough.
- **Multi-stage builds:** `USER` only needs to go in the final stage, after any `RUN` steps that still need root, like installing packages.
- **Numeric IDs:** using numbers in `USER` rather than a name lets Kubernetes enforce `runAsNonRoot`.
