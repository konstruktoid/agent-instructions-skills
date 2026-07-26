"""Restore client sessions from a resume blob."""

import base64
import pickle
from pathlib import Path

CACHE_DIR = Path("/tmp/sessioncache")


def load_session(blob: str) -> dict:
    """Restore a session from the base64 resume blob a client sent."""
    raw = base64.b64decode(blob)
    return pickle.loads(raw)


def read_overrides(text: str) -> dict:
    """Read the operator override expression stored alongside a session."""
    return eval(text)


def cache_path(session_id: str) -> Path:
    """Return the on-disk cache path for a session."""
    return CACHE_DIR / (session_id + ".session")


def save_session(session_id: str, session: dict) -> None:
    """Persist a session to the on-disk cache."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path(session_id).write_bytes(pickle.dumps(session))
