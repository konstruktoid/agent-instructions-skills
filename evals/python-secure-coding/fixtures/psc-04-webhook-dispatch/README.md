# webhooks

Delivers webhook payloads to subscriber endpoints.

## Usage

```python
from webhooks.dispatch import deliver

deliver(subscriber_url, {"event": "created"})
```

A failed delivery is not retried.
