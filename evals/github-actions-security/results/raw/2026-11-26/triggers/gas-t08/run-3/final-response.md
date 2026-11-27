I didn't change the Dockerfile. I found it at the repository root, but the request to read it was denied. I also don't have a tool in this session that can edit files.

To get it fixed, you can either:

1. **Allow the read and give me edit access**, and I'll make the change myself.
2. **Paste the Dockerfile here**, and I'll write the exact changes for you to apply.

The usual fix is to create a dedicated user with no login shell and switch to it before the app starts. On a Debian- or Ubuntu-based image it looks like this:

```dockerfile
# ... build and install steps that need root stay above this point ...

RUN groupadd --system --gid 10001 app \
 && useradd --system --uid 10001 --gid app --no-create-home --shell /usr/sbin/nologin app

COPY --chown=app:app . /app
WORKDIR /app

USER app:app

CMD [...]
```

How this fits depends on what's in your Dockerfile:
- **Alpine images:** use `addgroup -S -g 10001 app && adduser -S -u 10001 -G app -H -s /sbin/nologin app` instead.
- **Distroless images:** use the built-in `USER nonroot:nonroot`.
- **Ports:** a non-root user can't bind to ports below 1024, so if the app listens on 80 or 443, move it to a higher port such as 8080.
- **Write access:** if the app writes to particular folders (cache, uploads, logs), give `app` ownership of just those, not the whole filesystem.
- **Multi-stage builds:** the `USER` line only needs to go in the final stage.
