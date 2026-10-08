`ansible-lint` now passes under the `production` profile, but `make test` still fails in the molecule stage. The failure comes from the environment, not from the role, so the role has not been exercised in a container.

**Test result**
- **Lint:** `Passed: 0 failure(s), 0 warning(s)`. I did not touch `.ansible-lint`. Before my changes it reported 6 violations.
- **Molecule:** the run fails in the `destroy` step, before `converge` or `idempotence`. The error is `Failed to import the required Python library (requests)` on `/home/user/Code/Git/agent-instructions-skills/.venv/bin/python3`.
- **What I tried:** molecule's own Python has `requests` and `docker`, so I tried pointing `ANSIBLE_PYTHON_INTERPRETER` at it. It made no difference, because the localhost interpreter is still resolved to that `.venv`.
- **Not tried:** I did not install `requests` into that `.venv`, since that changes your environment. Installing it there, or running with a Python that has `requests` and `docker`, should let molecule proceed. I can do that if you want.

**Role fixes** (`nftables_base`)
- **Lockout:** the ruleset had a `drop` policy and never used `nftables_allowed_tcp_ports`, so SSH would have been blocked. It now accepts established/related traffic, loopback, and the configured TCP ports.
- **Variable names:** the role's variables now use the `nftables_base_` prefix (`nftables_base_default_policy`, `nftables_base_allowed_tcp_ports`, `nftables_base_ruleset_path`), as the linter requires. This renames the role's public variables, so any playbook that overrides the old names will need updating.
- **Idempotence:** the unconditional `nft -f` task is gone. The reload handler applies the ruleset, and a task now enables and starts the service.
- **Ruleset file:** the `copy` task sets owner, group and mode, and validates the ruleset with `nft -c` before writing it.
- **Check task:** it no longer uses a `shell` pipe to `wc`. It runs `nft list ruleset` with `changed_when: false`.
- **Platforms:** the role metadata listed only Debian, although the README says Debian and RedHat. I added EL 9 and changed the minimum version to `2.15.0`.

**Collection fixes**
- **Metadata:** `galaxy.yml` gained `repository`, `homepage`, `documentation`, `issues` and `tags`.
- **Changelog:** I added `CHANGELOG.md`.
- **Runtime:** `meta/runtime.yml` now uses `>=2.15.0`, which the linter requires.
- **README:** it now documents the role variables.

The nftables changes are untested beyond lint, and the `nft -c` validation has never run. I added the EL 9 platform without testing on it, since the molecule scenario only covers Debian bookworm. Nothing is committed.
