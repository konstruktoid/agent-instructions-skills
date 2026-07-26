"""Tests for fetcher.client."""

import pytest
from fetcher import Client
from fetcher.client import TransportError


def test_get_returns_the_transport_result():
    """A successful transport call is returned unchanged."""
    client = Client(lambda method, path: f"{method} {path}")
    assert client.get("/health") == "GET /health"


def test_get_retries_until_it_succeeds():
    """A transport that fails twice is retried until it succeeds."""
    calls = []

    def transport(method, path):
        calls.append(method)
        if len(calls) < 3:
            raise TransportError(path)
        return "ok"

    client = Client(transport)
    assert client.get("/health") == "ok"
    assert client.attempts == 3


def test_get_gives_up_after_the_attempt_limit():
    """A transport that always fails raises the last error."""

    def transport(method, path):
        raise TransportError(path)

    client = Client(transport)
    with pytest.raises(TransportError):
        client.get("/health")
    assert client.attempts == 3


def test_head_uses_the_head_method():
    """HEAD requests reach the transport as HEAD."""
    client = Client(lambda method, path: method)
    assert client.head("/health") == "HEAD"
