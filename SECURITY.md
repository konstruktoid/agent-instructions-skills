# Security policy

This repository publishes agent-facing content: skills, instructions documents, and agent
templates that a Claude Code plugin installs into other people's projects, where an agent reads
them and acts on them. The content is the attack surface, so this file covers both how to report a
problem in it and what it reads and sends when it runs.

## Contents

- Reporting a vulnerability
- Supported versions
- Withdrawing a bad version
- What this content reads and sends

## Reporting a vulnerability

Use GitHub private vulnerability reporting: the **Security** tab of this repository, then **Report
a vulnerability**. It is enabled. Issues and pull requests are public and are not the channel for
anything that should stay private until a fix exists.

A report is more useful with the file and line it concerns, since almost everything here is prose
that an agent acts on rather than code that runs.

This repository is maintained by one person. The commitment is an acknowledgement within **7
days** and a status update within **14 days** of the acknowledgement. Coordinated disclosure is
expected: a fix and its advisory are published together, and 90 days is the default before a
report is disclosed regardless.

## Supported versions

Fixes ship in the next release tag. There is no long-term support branch and no backporting: the
supported version is the most recent `v*` tag, and a consumer on an older tag moves forward to
receive a fix.

Release tags are protected against deletion and force update by
[.github/rulesets/release-tags.json](.github/rulesets/release-tags.json), so a published tag names
the same tree permanently. See the release process in [README.md](README.md).

## Withdrawing a bad version

A tag cannot be repointed here, by design, so a bad release is corrected forward rather than
rewritten:

1. Fix on `main` through a pull request, and cut a new tag.
2. Publish a GitHub advisory naming the affected tag and version, and what the content did.
3. State in the advisory which install form is affected. A consumer pinned to the affected tag has
   to move deliberately; a consumer who installed the unpinned marketplace form receives the fix
   at their next `/plugin update` and may already have received the problem the same way.
4. Rotate any credential the release path touched, and record what ran and when.

## What this content reads and sends

The statement below is what
[references/agent-content.md](skills/github/github-repository-security/references/agent-content.md)
asks every publisher of agent-facing content to provide, so that a reader can compare the claim
against the files.

**What ships.** Eight skills under `skills/`, six documents under `instructions/`, five agent
templates under `agent-templates/`, and the reference files each skill loads on demand. There are
no session hooks, no MCP server definitions, no slash commands, no installable subagents, and no
`.claude/settings.json`; `scripts/check_skills.py` fails the build when any of those appears at
the repository root. The eval harness under `evals/` is not part of any plugin and does not ship.

**Reads.** Files in the repository the agent is already working in: source, tests, CI workflows,
and the rule files a skill names, which are `CONTRIBUTING.md`, `CLAUDE.md`, `AGENTS.md`,
`.github/copilot-instructions.md`, and `.github/instructions/*.instructions.md`. Also
`${CLAUDE_PLUGIN_ROOT}/instructions/*.md`, which is this library's own content, and the output of
the commands below. No skill instructs reading a credential file, a shell profile, an environment
file, or cloud configuration. A `.env` file appears in this content only in rules about keeping
such files out of a commit and out of a log, never as something to open.

**Writes.** Files in the repository the agent is working in, and scratch directories created with
`mktemp -d` outside it, each named in the skill that creates one.

**Runs.** The target repository's own entry points, plus these by name: `ansible-lint`,
`molecule`, `ansible-test`, `ansible-galaxy`, `shellcheck`, `bash -n`, `shfmt`, `bats`, `pytest`,
`ruff`, `ty`, `pre-commit`, `actionlint`, `zizmor`, OpenSSF Scorecard, `gh`, `git`, and `docker`.
A skill that runs the target repository's own entry point runs whatever that repository has
configured, `pre-commit` hooks included.

**Sends.** Only what those commands send:

- `api.github.com` and the repository's own git remote, through `gh` and `git`.
- A container registry, through `docker run` of `rhysd/actionlint` on `docker.io`, pinned by
  digest, and of the OpenSSF Scorecard image on `gcr.io`, which `github-repository-security`
  asks to be resolved to a current release and pinned by digest before it runs.
- A Python package index, through `uvx` resolving `zizmor` at run time.
- `docs.github.com`, through the instruction in `github-repository-security` and
  `github-organization-governance` to check the current REST documentation where an endpoint
  fails or a field is absent. That one is a fetch written in prose rather than a command, which
  is the case `scripts/check_capabilities.py` names as the one it cannot detect: it is listed
  here because a reader comparing this statement against the files would not find it otherwise.
- Whatever the target repository's own dependency installation reaches, which this content does
  not choose.

Nothing is sent anywhere else. There is no telemetry, no callback to this repository or its
maintainer, and no URL built from file contents. The links in each skill's References section are
citations for a reader, not instructions to fetch anything.
