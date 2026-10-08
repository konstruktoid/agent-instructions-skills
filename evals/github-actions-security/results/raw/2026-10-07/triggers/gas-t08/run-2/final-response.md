I couldn't edit the Dockerfile. The Edit tool is disabled in this session, and I have no other tool that writes to local files. Here is the change to apply:

```dockerfile
FROM python:3.13-slim
RUN useradd --system --create-home --uid 10001 appuser
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
USER appuser
CMD ["python", "-m", "app"]
```

- **Install step:** `pip install` still runs as root, before `USER appuser`. Packages go into the system site-packages, which the unprivileged user can read.
- **Source ownership:** `COPY . .` leaves the files root-owned. That's fine if the app only reads them. If it writes under `/app`, use `COPY --chown=appuser:appuser . .` and make sure `/app` is writable by that user.
- **Fixed UID:** `10001` is explicit so that Kubernetes `runAsNonRoot` checks and volume permissions behave predictably.

I haven't built the image or run the app as the new user. If you enable file editing, or tell me to apply it another way, I'll make the change.
