`complete_reset()` is implemented in `src/accounts/reset.py:58-74`:

- **Verifies** the token against every outstanding token issued for the account.
- **Expires** tokens 30 minutes after issue (`TOKEN_LIFETIME`, tracked per-token via a `datetime` recorded in `request_reset`).
- **Single-use**: a successful reset clears all of that account's outstanding tokens, including the one just used.
- **Clears other tokens**: since all tokens for the account are cleared on success, any earlier reset links sent for the same account are invalidated too.
- **Never raises**: unknown, wrong, expired, or reused tokens simply return `False`.

`check_token` was updated the same way (list of tokens, expiry-aware) to stay consistent. README now documents the full request → check → complete flow and the token rules. `ruff check .` and `ty check .` both pass, and I manually exercised unknown/wrong/expired/reused/multi-token scenarios to confirm correct behavior.
