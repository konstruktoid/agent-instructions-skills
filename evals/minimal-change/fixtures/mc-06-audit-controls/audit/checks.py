"""Configuration checks required by POLICY.md."""


def check_config(cfg):
    """Return the ids of the controls in POLICY.md that cfg violates."""
    failed = []
    audit = cfg.get("audit", {})
    if audit.get("enabled") is not True:
        failed.append("AL-1")
    if audit.get("destination", "stdout") == "stdout":
        failed.append("AL-2")
    return failed
