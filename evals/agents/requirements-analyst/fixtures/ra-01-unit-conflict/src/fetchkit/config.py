"""Process-wide settings, read once at import."""

import os

TIMEOUT_MS = int(os.environ.get("FETCHKIT_TIMEOUT_MS", "30000"))
RETRIES = int(os.environ.get("FETCHKIT_RETRIES", "2"))
