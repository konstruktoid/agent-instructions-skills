# accounts

Account password reset flow.

## Usage

```python
from accounts.reset import request_reset

token = request_reset("user@example.com")
```

Password storage and token comparison live in `accounts.crypto`, which the reset
flow calls rather than hashing or comparing anything itself. Issuing a token and
checking one are implemented; completing a reset is not.
