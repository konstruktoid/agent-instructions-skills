`make test` did not pass. Lint passes, but the molecule scenario fails because of the environment, so I couldn't verify the role against a container.

**What I fixed**
- **`galaxy.yml`**
  - Added `repository`, `documentation`, `homepage` and `issues`, all pointing at the GitHub URL from the README.
  - Added `tags`: networking, security and linux.
- **`CHANGELOG.md`**: new file. `galaxy[no-changelog]` required one.
- **`meta/runtime.yml`**: `requires_ansible` raised from `>=2.15` to `>=2.17.0`, because 2.15 is no longer a supported version for the linter.
- **`roles/nftables_base/defaults/main.yml` and `tasks/main.yml`**: renamed all variables to use the `nftables_base_` prefix.
- **`roles/nftables_base/tasks/main.yml`**
  - The ruleset file now has an owner, group and mode (`0644`).
  - The `nft -f` command and the rule-count check now have `changed_when: false`.
  - The pipe in the shell task now sets `pipefail`.
  - The ruleset template previously ignored `allowed_tcp_ports`, so with a drop policy it would have locked out SSH. It now loops over the ports, and I also added loopback and established/related accepts.
- **`roles/nftables_base/meta/main.yml`**
  - `min_ansible_version` is now 2.17.
  - Added an EL platform entry, since the README says RedHat is supported. The role has not been tested on RedHat.

The `.ansible-lint` configuration is unchanged.

**Test result**
- **`ansible-lint .`**: passes the `production` profile with 0 failures. It started with 12.
- **`molecule test -s default`**: fails. The docker driver's `destroy.yml` and `create.yml` stop with "Failed to import the required Python library (requests)" on `/tmp/eval-tools/ansible-core/bin/python`. Molecule's own interpreter is a different Python from the one ansible-core runs under.
- **Not checked**: converge, idempotence and the role's behaviour in a container never ran.

To get a full run, install `requests` (and the `docker` Python library) into the ansible-core environment, or point molecule at an interpreter that has them. I didn't change the tool environment myself. After that, `make test` should be rerun.
