I fixed the role and the collection metadata, and `ansible-lint` now passes. But `make test` fails: the molecule step never gets as far as running the role, so the role is untested.

**Test result**
- **`ansible-lint .`:** the `production` profile passes with no failures and no linter config changes. It had 12 failures before.
- **`molecule test -s default`:** fails in the very first `destroy` step, before any `create` or `converge`. The Docker modules in molecule's playbook can't import the Python `requests` library. They run under `/tmp/eval-tools/ansible-core/bin/python`, and that environment doesn't have `requests`.
- I didn't install anything into that toolchain. Installing `requests` into it, or pointing `ansible_python_interpreter` at an interpreter that has it, should unblock the run. Then rerun `make test`.
- Until that happens, the converge and idempotence of the role changes are unverified.

**Role changes (`nftables_base`)**
- **Variable names:** I renamed all variables to the `nftables_base_` prefix, including the registered result.
- **Allowed ports:** `nftables_base_allowed_tcp_ports` was defined but never used. With a drop policy that would have locked out SSH. The ruleset now accepts established/related traffic, loopback and the listed TCP ports. It also starts with `flush ruleset`.
- **File permissions:** the ruleset file is now owner root, group root, mode 0644.
- **Load step:** I replaced the non-idempotent `nft -f` command with an enable-and-start `service` task. The existing reload handler now applies ruleset changes.
- **Active ruleset check:** it now runs plain `nft list ruleset` with `changed_when: false`, so the unsafe `| wc -l` pipe is gone. I haven't confirmed that command runs on a real host.
- **Platforms:** the README says Debian and RedHat, but the role metadata listed only Debian. I added EL 9 to the role metadata. Nothing has tested the role on EL 9, and the molecule scenario only covers Debian bookworm.

**Collection metadata**
- **`galaxy.yml`:** added `repository` (the URL from the README) and `tags` (networking, security, linux).
- **`CHANGELOG.md`:** new file.
- **`meta/runtime.yml`:** `requires_ansible` moved from `>=2.15` to `>=2.16.0`, because 2.15 is no longer a supported version. I also bumped the role's `min_ansible_version` to 2.16.

I haven't committed anything.
