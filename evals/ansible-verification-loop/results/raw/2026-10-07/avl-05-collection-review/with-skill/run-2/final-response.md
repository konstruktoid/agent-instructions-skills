`make test` failed, so the change is not fully verified. The lint half passes, but the molecule scenario never ran because of a problem in the molecule setup on this machine.

**Test result**
- **Lint:** `ansible-lint .` passes under the unchanged `production` profile. Before my changes it reported 12 failures.
- **Molecule:** the run stopped in the docker driver's `destroy` step. The Python environment molecule uses (`/home/user/Code/Git/agent-instructions-skills/.venv`) has no `requests` library, so the driver's modules can't import it. I did not run converge, idempotence or verify.
- **Not tried:** installing `requests` into that shared virtualenv would probably fix it, but I didn't change your environment without asking. Tell me if you want me to, then I'll rerun.
- **Artifact:** I built the collection and read its file list. No local state is in it. The only entries not tracked by git are the files I added, which aren't committed yet, plus `MANIFEST.json` and `FILES.json`.

**Role fixes**
- **Lockout risk:** the ruleset set the input policy to `drop` but never used `nftables_allowed_tcp_ports`. It also allowed no loopback or established traffic, so applying it would have cut off SSH. It now accepts established/related traffic, loopback and the configured ports.
- **Variable names:** I renamed the variables to carry the `nftables_base_` prefix, which is what lint requires. Anything outside this repo that sets the old names needs updating.
- **Ruleset file:** it now has owner, group and mode `0600`. The file is checked with `nft -c` before it is written.
- **Command tasks:** I gave them `changed_when: false` and replaced the `nft list ruleset | wc -l` pipe with `nft list ruleset`. The registered result is now `nftables_base_active_ruleset`.
- **Argument spec:** I added `meta/argument_specs.yml` and a README variables table.
- **Platforms:** the README says Debian and RedHat, but `meta/main.yml` listed only Debian. I added EL 9, which is untested because the molecule scenario only covers Debian.

**Collection metadata**
- **`galaxy.yml`:**
  - I added `repository` and `tags` (`security`, `networking`).
  - I extended `build_ignore` to cover `.github`, `.gitignore`, `.ansible-lint`, `.ansible`, `.cache`, `.venv`, `.env`, `molecule`, `molecule-logs`, `Makefile`, `*.log` and `*.tar.gz`.
- **`.gitignore`:** I created it. There wasn't one.
- **`CHANGELOG.md`:** I added it, because lint requires a changelog.
- **`meta/runtime.yml`:** it now says `>=2.15.0`. The old `>=2.15` wasn't accepted.

I did not edit `.ansible-lint`.
