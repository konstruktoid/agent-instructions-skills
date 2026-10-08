"""Requests to the user service."""

import json
import urllib.request

BASE_URL = "https://users.internal.example"


def build_url(user_id: int) -> str:
    """Return the record URL for user_id."""
    return f"{BASE_URL}/users/{user_id}"


def fetch(user_id: int) -> dict:
    """Return the user record for user_id."""
    with urllib.request.urlopen(build_url(user_id), timeout=10) as response:
        return json.loads(response.read())
