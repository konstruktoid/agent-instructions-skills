`deliver` now uses a 5-second timeout per request and retries failed deliveries up to 3 times, so it makes at most 4 attempts. `ruff check`, `ruff format --check` and `ty check` all pass. There are no tests in the repo, so I checked the retry behaviour with a throwaway local HTTP server. That check showed:
- A 503 followed by a success took 3 attempts and ended with 200.
- A persistent 500 took 4 attempts.
- A 404 took 1 attempt.
- A refused connection took 4 attempts.

Backoff waits 1s, 2s and 4s between attempts. Connection errors, timeouts and 5xx responses are retried, and 4xx is final. All the changes are in `src/webhooks/dispatch.py` and `README.md`.

**Recording attempts:** a new `deliver_with_result(url, payload)` returns a `DeliveryResult`. Its `attempts` list holds one entry per try, each with a number, status and error. It also has `.status` and `.succeeded`, and it doesn't raise on delivery failure.

**Behaviour change in `deliver`:** it still returns the status code on success. It now raises `DeliveryError` when delivery fails, and the error carries the same attempt record in `.result`. Before, a 4xx or 5xx raised an `HTTPError` from `urlopen`. Any caller that catches `HTTPError` will need updating.

**Token no longer logged:** I changed the log line to record the delivery, URL, attempt number and outcome. It no longer writes `SIGNING_TOKEN` to the logs.

I left these other problems in `dispatch.py` alone because they're outside what you asked for:
- The signing token is hardcoded in the source.
- `sign` doesn't actually sign anything: it's the token plus the payload length, so anyone who sees one signature can forge others.
- Delivery IDs come from `random` rather than a secure source.
- Subscriber URLs aren't validated, so a subscriber could point a delivery at an internal address.

I can fix those in a follow-up if you want.
