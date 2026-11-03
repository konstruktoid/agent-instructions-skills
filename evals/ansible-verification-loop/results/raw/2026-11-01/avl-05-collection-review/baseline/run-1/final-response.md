I fixed the role and the collection metadata. `ansible-lint .` now passes the production profile, but `make test` still fails at the molecule step because of an environment problem. The role itself never ran, so it is untested.

**Test result**
- **`ansible-lint`:** it started with 12 failures and now has 0. I didn't touch `.ansible-lint`.
- **`molecule test`:** it failed in the `destroy` step, before the role was applied. The docker driver playbook needs the Python `requests` library, and the Python that Ansible uses (`/tmp/eval-tools/ansible-core/bin/python`) doesn't have it. I didn't install anything or change the toolchain, so the molecule scenario is unverified. Installing `requests` there, or pointing molecule at a Python that has it, should unblock the run.

**Role (`nftables_base`)**
- **Ports:** `nftables_allowed_tcp_ports` was defined but never used, so the generated ruleset dropped everything, including SSH. The ruleset now accepts established/related traffic, loopback, and the configured TCP ports.
- **Variable names:** I renamed every variable to the `nftables_base_` prefix, which `ansible-lint` requires.
- **File permissions:** the ruleset file now has owner `root`, group `root` and mode `0644`.
- **Loading the ruleset:** the always-changed "load now" task is now a handler, `Load nftables ruleset`, notified when the file changes. This makes the role idempotent.
- **Ruleset check:** the `shell … | wc -l` task is now a plain `nft list ruleset` marked `changed_when: false`.
- **Platforms:** the README says Debian and RedHat, but the role metadata only listed Debian. I added EL 9, which I haven't run.

**Collection metadata**
- **`galaxy.yml`:** I added `repository` and `tags` (networking, security, linux), and excluded `molecule` from the build.
- **`CHANGELOG.md`:** new file.
- **`meta/runtime.yml`:** `requires_ansible` is now `>=2.16.0`, because `>=2.15` is no longer a supported version for the linter. I made the same change to the role's `min_ansible_version`.

Nothing is committed.
