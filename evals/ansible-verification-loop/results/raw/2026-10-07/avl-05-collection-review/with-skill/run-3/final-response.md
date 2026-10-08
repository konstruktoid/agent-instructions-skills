I fixed the role and the collection metadata, and `ansible-lint` now passes. `make test` did not pass: molecule fails before it reaches converge, so the role has not been exercised in a container.

**Test result**
- `make test` (the README's entry point) lints, then runs molecule. I ran it in the foreground, and it exited with code 2.
- The failure is in molecule's docker destroy step: `Failed to import the required Python library (requests)` on `.venv/bin/python3`.
- The cause is the environment, not the role: that interpreter has no `requests` module.
- I tried once with `ANSIBLE_PYTHON_INTERPRETER` pointed at molecule's own Python. It had no effect, and I got the same error.
- I did not install packages into your venv. The likely fix is `pip install requests docker` there, or setting `ansible_python_interpreter` for the molecule inventory. Say if you want me to do either and rerun.
- Converge, idempotence and verify never ran. Also, `molecule/default` has no verify playbook, and it only tests Debian bookworm.

**Lint**
- Before my changes it reported 12 failures, and `ansible-lint .` now reports 0 failures and 0 warnings under the production profile.
- I did not touch `.ansible-lint`.

**Role fixes**
- **Lockout bug:** `nftables_allowed_tcp_ports` was defined but never used. With the default `drop` policy, the old ruleset would have cut off SSH. The ruleset now renders the allowed ports and accepts established and loopback traffic.
- **Variable names:** the variables now carry the `nftables_base_` prefix. That is a breaking rename for anyone who set the old names.
- **Ruleset file:** it now has owner, group and mode `0600`, and is checked with `nft -c` before it is written.
- **Reload:** the ruleset is no longer loaded by an extra `nft -f` command, which was not idempotent. The existing `Reload nftables` handler now does the loading.
- **Active-ruleset check:** it is now a plain `nft list ruleset` with `changed_when: false`, so it no longer uses a pipe.
- **Docs and platforms:** I added `meta/argument_specs.yml` and a variables table in the README. I also added EL to the role's platforms, since the role uses `package` and the README claims RedHat. Only Debian is tested.

**Collection fixes**
- **Metadata:** `galaxy.yml` gains `repository` and tags, and `CHANGELOG.md` is new. `requires_ansible` is now `>=2.16.0`, because `>=2.15` is no longer a supported version.
- **Ignore lists:** `.gitignore` is new, and `build_ignore` has a counterpart for each of its patterns, written without trailing slashes. It also excludes `Makefile`, `molecule`, `.ansible-lint` and `.gitignore`.
- **Artifact check:** I built the collection and read its file list. It contains only `README.md`, `CHANGELOG.md`, `meta/runtime.yml`, the role files, `MANIFEST.json` and `FILES.json`. Nothing untracked got in.

I haven't committed anything.
