# Audit logging policy

A service meets this policy when its configuration satisfies every control below. A control
that is satisfied by the shipped defaults is still checked against the configuration supplied.

| Id | Control | Rule on `cfg["audit"]` |
|----|---------|------------------------|
| AL-1 | Audit logging is enabled | `enabled` is `True` |
| AL-2 | Records leave the process | `destination` is not `"stdout"` |
| AL-3 | Records are kept for a year | `retention_days` is an integer of at least 365 |
| AL-4 | Records identify who did what | `fields` includes `user`, `action`, `timestamp`, and `outcome` |
| AL-5 | Records are protected from edits | `tamper_protection` is `True` |
