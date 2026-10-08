I fixed the role and the collection metadata, and `ansible-lint` now passes on the production profile. `make test` still fails, though. The failure is in the molecule step, because the molecule docker driver can't start in this environment.

**What failed:** molecule's `destroy` and `create` playbooks stop with `Failed to import the required Python library (requests)`. Ansible is using `/home/user/Code/Git/agent-instructions-skills/.venv/bin/python3`, and that interpreter has no `requests`. The converge step never ran, so the role has not been tested in a container.

I did not install anything into that venv or change the interpreter setting. That's your environment, and you'd need to decide how to fix it. Installing `requests` there, or pointing `ansible_python_interpreter` at a Python that has it, should be enough. I haven't tried either.

**Role (`roles/nftables_base`):**
- **Variable names:** the defaults and the registered variable now use the `nftables_base_` prefix. Anyone overriding the old `nftables_*` names will need to rename them.
- **Ruleset file:** it now sets owner, group and mode `0644`.
- **Allowed ports:** `nftables_base_allowed_tcp_ports` was defined but never used. The ruleset now accepts loopback and established/related traffic, plus those TCP ports.
- **Command and shell tasks:** both are marked `changed_when: false`, and the shell task uses `pipefail` with bash.
- **Role metadata:** I added an EL 9 platform entry, since the README says Debian and RedHat. I also raised `min_ansible_version` to 2.17.

**Collection:**
- **`galaxy.yml`:** I added `repository`, `homepage`, `issues` and `tags`. The URLs are taken from the README and I haven't checked that they exist.
- **`meta/runtime.yml`:** `requires_ansible` is now `>=2.17.0`, because 2.15 is no longer a supported version.
- **Changelog:** I added `CHANGELOG.md`. I wrote its 1.2.0 entry myself, so check the wording.

I did not change `.ansible-lint`.

The EL 9 platform entry in the role metadata is not covered by the molecule scenario, which only tests Debian bookworm.
