`make test` failed. `ansible-lint` now passes at the `production` profile, but the molecule step errors out before it tests the role, so the role is not verified.

**Test result**
- **Lint:** `ansible-lint .` went from 12 failures to 0. I didn't change `.ansible-lint`.
- **Molecule:** the `default` scenario fails in the docker driver's `destroy` playbook. The error is `Failed to import the required Python library (requests)`. Molecule's docker playbooks run on the `.venv` Python (`/home/user/Code/Git/agent-instructions-skills/.venv/bin/python3`), which has no `requests`. The converge step never ran, so the role has not been exercised in a container. I'd expect it to pass once `requests` is installed in that environment, but that is untested.
- **Environment fix I did not make:** installing `requests` there (or pointing `ansible_python_interpreter` at a Python that has it) is a change outside the repo, so I left it for you.

**Role fixes (`roles/nftables_base`)**
- **Variable names:** all variables now carry the `nftables_base_` prefix (defaults, tasks and the registered result).
- **Ports:** `nftables_base_allowed_tcp_ports` was defined but never used. The ruleset template now emits a `tcp dport { … } accept` rule from it. Before this, the default `drop` policy would have blocked SSH.
- **File permissions:** the ruleset file now sets `owner`, `group` and `mode: "0644"`.
- **Changed state:** the two `nft` command tasks have `changed_when: false`.
- **Shell pipe:** the shell task uses `set -o pipefail` with bash.
- **Metadata:** `min_ansible_version` is now `2.18`.

**Collection fixes**
- **Ansible version:** `meta/runtime.yml` now requires `>=2.18.0`. The old `>=2.15` is no longer a supported version, and the linter rejects it.
- **`galaxy.yml`:** I added `repository` (taken from the README) and `tags` (`networking`, `security`, `linux`).
- **`CHANGELOG.md`:** added, with a stub entry for 1.2.0.

**Open items**
- The README says "Debian and RedHat hosts", but the role's `meta/main.yml` lists only Debian bookworm. The role also writes to `/etc/nftables.conf`, which isn't the RedHat default. I left both alone.
- Nothing is committed.
