"""Defaults that new deployments start from."""

DEFAULTS = {
    "audit": {
        "enabled": True,
        "destination": "file:/var/log/audit.log",
        "retention_days": 400,
        "fields": ["user", "action", "timestamp", "outcome"],
        "tamper_protection": True,
    }
}
