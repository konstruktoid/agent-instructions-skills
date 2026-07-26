"""Client that retries a transport call."""

MAX_ATTEMPTS = 3


class TransportError(Exception):
    """Raised when the transport fails."""


class Client:
    """Calls a transport, retrying a fixed number of times."""

    def __init__(self, transport) -> None:
        """Store the transport callable."""
        self.transport = transport
        self.attempts = 0

    def get(self, path: str) -> str:
        """Fetch a path, retrying on transport failure."""
        last_error = None
        for _ in range(MAX_ATTEMPTS):
            self.attempts += 1
            try:
                return self.transport("GET", path)
            except TransportError as error:
                last_error = error
        raise last_error

    def head(self, path: str) -> str:
        """Issue a HEAD for a path, retrying on transport failure."""
        last_error = None
        for _ in range(MAX_ATTEMPTS):
            self.attempts += 1
            try:
                return self.transport("HEAD", path)
            except TransportError as error:
                last_error = error
        raise last_error
