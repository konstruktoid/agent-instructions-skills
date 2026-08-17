# Agent Instructions and Skills

This repository is a library of reusable guidance for AI coding agents. It contains three kinds of
material: instructions documents that describe how output in a given domain should be produced,
Claude Code skills that describe a repeatable procedure an agent should follow, including when to
follow it and how to verify the result, and agent templates that describe who runs the work, with
which model and which tools.

## Repository structure

```text
instructions/     Domain-specific writing and coding standards (plain Markdown, no frontmatter)
skills/           Claude Code skills, one directory per skill: skills/<category>/<name>/SKILL.md
agent-templates/  Copy-and-adapt Claude Code subagent definitions, one flat file per agent
evals/            Measurements of whether each skill changes agent output, and what it triggers on
scripts/          Checks that enforce this repository's own authoring rules
.claude-plugin/   Marketplace manifest, so other projects can install the skills as plugins
```

### instructions/

Each file in `instructions/` sets the objective, required style, and a quality checklist for one
kind of output. These documents are not auto-discovered by any tool. Use them by referencing the
relevant file from a project's `CLAUDE.md` or `AGENTS.md`, for example:

```markdown
When writing Python, follow instructions/python_coding_instructions.md.
```

Or by pointing an agent at the file directly at the start of a task.

Current instructions documents:

| File | Covers |
|------|--------|
| `python_coding_instructions.md` | Passing `ruff` and `ty` cleanly, plus the judgment calls those tools cannot make. |
| `bash_coding_instructions.md` | Passing `shellcheck`, `bash -n`, and the repository's formatter cleanly, plus the layout, naming, and judgment rules those tools cannot enforce. |
| `written_language_instructions.md` | Formal, concise, precise written style for any prose output. |
| `overview_document_instructions.md` | Structure and content for a repository-level overview document. |

### skills/

Each skill is a `SKILL.md` file with a YAML frontmatter block (`name`, `description`) followed by
a fixed set of sections, listed under [Adding new material](#adding-new-material). The
`description` field is what a Claude Code agent uses to decide whether a skill applies to the
current task, so it should state concretely what the skill is for and when it should trigger.

A skill may keep longer material in a `references/` directory next to its `SKILL.md`, linked by
relative path from the skill body. `SKILL.md` then stays a triage layer: the steps, the verify
loop, and an index pointing at the detail to read for the change at hand. An agent loads a
reference file only when it applies, instead of carrying every category of detail in context.

Once a skill is available to Claude Code, it is invoked automatically when its `description`
matches the current task, or explicitly by name. See
[Using this library from another project](#using-this-library-from-another-project) for how to
make it available without copying it.

Current skills:

| Skill | Path | Covers |
|-------|------|--------|
| `ansible-verification-loop` | `skills/ansible/ansible-verification-loop/SKILL.md` | Reviewing or modifying Ansible roles and collections, verified through the repository's own lint/test loop. |
| `bash-secure-scripting` | `skills/bash/bash-secure-scripting/SKILL.md` | The `shellcheck`/`bash -n` baseline from `bash_coding_instructions.md`, extended with the stability and security properties a linter cannot verify: strict-mode semantics, cleanup on every exit path, untrusted input and injection, `PATH` and environment control, temporary files, and credentials, run through a bounded verify-fix loop. |
| `bash-testing` | `skills/bash/bash-testing/SKILL.md` | Adding or updating coverage for a shell change: discovering and matching the repository's existing framework (bats-core, shunit2, or plain scripts), making a script testable, covering exit codes and failure paths, and running the suite through a bounded verify-fix loop. |
| `github-actions-security` | `skills/github/github-actions-security/SKILL.md` | Authoring and reviewing GitHub Actions workflows and actions: least-privilege `GITHUB_TOKEN` permissions, dependencies pinned by commit SHA to the latest published release, injection-safe handling of untrusted event data, safe triggers and runners, and structures that scale across repositories, run through a bounded verify-fix loop with `actionlint` and `zizmor`. |
| `python-secure-coding` | `skills/python/python-secure-coding/SKILL.md` | The `ruff`/`ty` baseline from `python_coding_instructions.md`, extended with Python-specific security best practices aligned to the OWASP Top 10:2025 (input handling, deserialization, secrets, subprocess/SQL/crypto usage, SSRF, dependency hygiene), run through a bounded verify-fix loop. |
| `python-testing` | `skills/python/python-testing/SKILL.md` | Adding or updating pytest coverage for a Python change: discovering and matching the repository's existing test layout, deciding when a test is required, and running the suite through a bounded verify-fix loop. |

### agent-templates/

An agent template is a Claude Code subagent definition: a Markdown file with YAML frontmatter that
gives the agent its own context window, system prompt, `model:`, and `tools:` allowlist. Claude
Code loads subagents from a project's `.claude/agents/` directory or from `~/.claude/agents/`,
never from this library's directory.

These files are templates, not installable agents. An agent definition encodes per-repository
policy: what a model costs there, which tools are trusted there, which commands its verify loop
runs there. Copy one into the consuming project's `.claude/agents/` and edit it. Do not symlink
it. Divergence between the copy and this library is the intended outcome, which is the opposite of
the rule for `instructions/` and `skills/`.

Two frontmatter fields must be set by whoever copies a template:

- `model:`. Every template ships `model: inherit`, so a fresh copy pins no model of its own and
  runs on whatever the main conversation uses. Pin a stronger model for review-heavy agents, or a
  cheaper one for agents that apply a fixed checklist.
- `tools:`. Every template ships the smallest allowlist its work needs. Widen or narrow it against
  what the project trusts the agent to do. Frontmatter comments in each template state what to
  consider changing and why.

Each template is a thin wrapper. Its system prompt names the instructions document or skill that
holds the substance and points at it by path, rather than restating it. What the agent file adds
is routing and policy: which model, which tools, which scope, and what to report back.

Current templates:

| Template | Wraps | Notes |
|----------|-------|-------|
| `ansible-reviewer.md` | `skills/ansible/ansible-verification-loop` | Needs `Bash` for `ansible-lint` and the target repository's test entry point. Consider pinning a strong model. |
| `python-security-reviewer.md` | `skills/python/python-secure-coding` | Needs `Bash` for `ruff` and `ty`. Consider pinning a strong model. |
| `prose-editor.md` | `instructions/written_language_instructions.md` | `Read` and `Edit` only, no `Bash`. Candidate for a cheaper model. Needs the submodule, since it references an instructions document rather than a skill. |

The directory is named `agent-templates/` rather than `agents/` deliberately. Claude Code
auto-discovers an `agents/` directory at a plugin's root, and every plugin here is sourced
from the repository root, so templates placed in `agents/` would install into every consuming
project as live subagents, adding their descriptions to every session. That inverts the
copy-and-adapt rule, so the name that triggers discovery is avoided. Neither omitting the `agents`
field from a marketplace entry nor setting it to an empty list suppresses the discovery.
`scripts/check_skills.py` fails if an `agents/` directory reappears at the repository root.

## Using this library from another project

Agent templates are the exception to everything in this section: copy them, as described in
[agent-templates/](#agent-templates). For `instructions/` and `skills/`, a consuming project
should not copy the files or write its own version of them. Use one of the mechanisms below, each
of which keeps a single upstream copy that can be updated in place.

### Skills, as a Claude Code plugin

This repository is its own plugin marketplace. The skills are grouped into four plugins so a
project installs only what it needs:

| Plugin | Skills |
|--------|--------|
| `python-standards` | `python-secure-coding`, `python-testing` |
| `bash-standards` | `bash-secure-scripting`, `bash-testing` |
| `ansible-standards` | `ansible-verification-loop` |
| `github-standards` | `github-actions-security` |

From inside Claude Code, in the consuming project:

```shell
/plugin marketplace add konstruktoid/agent-instructions-skills
/plugin install python-standards@konstruktoid
/reload-plugins
```

The same operations exist as `claude plugin marketplace add` and `claude plugin install` outside a
session. Plugin skills are namespaced by plugin name, so `python-secure-coding` is invoked as
`/python-standards:python-secure-coding`, and Claude still triggers it automatically when the
task matches its `description`.

Installing the plugin brings the whole library along, `instructions/` included, so the skills
resolve their own references to `instructions/python_coding_instructions.md` without the project
doing anything.

To update to the current upstream state:

```shell
/plugin marketplace update konstruktoid
/plugin update python-standards
```

The plugin entries declare no `version`, so every commit here counts as a new version and an
update always fetches the current default branch.

### For a whole team, through project settings

Commit `.claude/settings.json` in the consuming repository so members are prompted to install the
plugins when they trust the project folder:

```json
{
  "extraKnownMarketplaces": {
    "konstruktoid": {
      "source": {
        "source": "github",
        "repo": "konstruktoid/agent-instructions-skills"
      }
    }
  },
  "enabledPlugins": {
    "python-standards@konstruktoid": true
  }
}
```

Add `"ref": "<branch-or-tag>"` next to `repo` to pin the team to a fixed branch or tag rather
than tracking the default branch. A marketplace source accepts a branch or tag, not a commit SHA.

### Instructions documents, and non-plugin setups

The files in `instructions/` are plain Markdown that no tool auto-discovers. The skills read them
on their own once the plugin is installed, but a project that wants an instructions document
applied outside a skill, for example a prose style that should hold for all output, needs a path
it can reference. A submodule gives it one, and works for agents and tools that have no plugin
mechanism at all:

```sh
git submodule add https://github.com/konstruktoid/agent-instructions-skills .agent-standards
```

Then reference the file by path from the project's `CLAUDE.md` or `AGENTS.md`:

```markdown
When writing Python, follow .agent-standards/instructions/python_coding_instructions.md.
When writing shell, follow .agent-standards/instructions/bash_coding_instructions.md.
When writing prose, follow .agent-standards/instructions/written_language_instructions.md.
```

A submodule pins an exact commit, which is recorded in the consuming repository and updated
deliberately with `git submodule update --remote`. Projects using Claude Code without plugins can
also expose the skills from the same submodule:

```sh
mkdir -p .claude/skills
ln -s ../../.agent-standards/skills/python/python-secure-coding .claude/skills/python-secure-coding
```

Do not reference `${CLAUDE_PLUGIN_ROOT}` from a project's own `CLAUDE.md`. That variable is
substituted in plugin content, such as a skill body, and does not resolve in project files.

### Agent templates, by copying

Agent templates are copied by design, whichever of the mechanisms above the project already uses:

```sh
mkdir -p .claude/agents
cp .agent-standards/agent-templates/prose-editor.md .claude/agents/prose-editor.md
```

Then edit the copy: set `model:` and `tools:`, remove the frontmatter comments once the choices
are made, and resolve the reference the system prompt points at. A template that wraps a skill
offers one row per install mechanism, plugin or submodule, and expects the row that does not apply
to be deleted.

A copied template is project content, not plugin content, so `${CLAUDE_PLUGIN_ROOT}` does not
substitute in it. Under a plugin install a template reaches a skill by invoking it under its
namespaced name, such as `ansible-standards:ansible-verification-loop`, and the `skills:`
frontmatter field can preload that skill at startup instead. A template that references an
instructions document directly has no such name to use, so it needs the submodule.

Claude Code reloads `.claude/agents/` within a few seconds of a file changing. Creating the
directory for the first time during a session is the exception and needs a restart.

### Copying, as a last resort

For `instructions/` and `skills/`, copy a file only when the consuming environment can use neither
a plugin nor a submodule, such as an air-gapped checkout. Record the upstream commit the copy came
from, so the drift is visible later. A copy stops receiving fixes the moment it is made, which is
the outcome the mechanisms above exist to avoid.

## Adding new material

- Add a new instructions document to `instructions/` when the goal is a style or quality standard
  for a category of output. Follow the existing files' structure: Objective, required/avoid style
  rules, and a Quality Checklist.
- Add a new skill to `skills/<category>/<name>/SKILL.md` when the goal is a repeatable procedure
  with a verification step. Write the `description` field so it states precisely which tasks
  should trigger the skill. Use the section order the existing skills share, so an agent finds
  the same things in the same place in every skill:

  ```text
  Purpose, When to use this, When NOT to use this, Steps,
  [any skill-specific sections], Verify, Verification checklist, References
  ```

- List every new skill in `.claude-plugin/marketplace.json`, under the plugin for its category.
  A skill that is not listed there is invisible to any project that installs this library as a
  plugin. `scripts/check_skills.py` fails when a skill is unlisted, listed twice, or points at a
  path with no `SKILL.md`.
- Write `description` in third person: lead with what the skill does, close with when to use it
  (see Anthropic's [skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)).
  Avoid first/second person ("I can help you...", "Use this to..."), keep it under 1,024
  characters, and keep the SKILL.md body under 500 lines, moving longer material into files it
  links to directly.
- Give every `references/*.md` file over 100 lines a `## Contents` section listing its own
  headings, placed after the opening paragraph and before the first section. The same best
  practices document asks for one, because an agent previewing a long file with a partial read
  otherwise sees only its first screen and cannot tell what else the file covers.
  `scripts/check_skills.py` fails when a long reference file has no `Contents` section, when a
  section already precedes it, and when the entries do not match the headings that follow them,
  since a list that drifts from the document is worse than none.
- For any skill with a verify-then-fix cycle, bound the retries explicitly and define what one
  attempt is: one full fix-and-rerun cycle. This repo baselines the bound at 3 attempts, lets an
  agent continue while each cycle produces strictly fewer findings, and requires it to stop early
  when the loop oscillates without progress. On stopping, the skill must require reporting the
  failing check and its output to the user, instead of looping silently or declaring success
  unverified. Every skill here uses the same wording for this loop; copy it rather than
  paraphrasing, so the bound means the same thing everywhere. `scripts/check_skills.py` compares
  the block against the canonical wording and fails on any rewording, so this is enforced rather
  than left to whoever copied it last. A testing skill may write "failures" for "findings" and
  "failing test" for "failing check", since it counts failing tests; the checker folds those two
  spellings together and holds every other word exactly.
- When a skill extends or depends on an instructions document, cross-reference it by path in both
  directions, as done between `python_coding_instructions.md` and `python-secure-coding`. Do not
  copy the shared material into both files. The instructions document is the single source of
  truth; the skill carries a short summary and a pointer to it.
- Add a new agent template to `agent-templates/<name>.md` when the goal is to give a kind of work
  its own context window, model, and tool allowlist. One flat file per agent: nothing
  auto-discovers these from the library, so a directory per agent buys nothing. Keep the file a
  thin wrapper, naming the instructions document or skill that holds the substance and pointing at
  it by path rather than restating it. What belongs in the agent file is routing and policy:
  scope, and what the agent reports back to the main conversation.
- Ship agent templates with neutral defaults, `model: inherit` and the smallest `tools:` allowlist
  the work needs, so copying one pins no model on the consumer and grants no broad tool access.
  State in frontmatter comments what to consider changing and why, for example pinning a stronger
  model for a review-heavy agent, or adding `Bash` only because the verify loop needs it.
- A template aimed at a cheaper model needs its verification spelled out rather than assumed. Keep
  what it must follow short and checklist-like, and reuse this repository's bounded verify-fix
  wording, adapted to whatever one attempt means for that agent.
- Never place agent templates in a directory named `agents/` at the repository root. Claude Code
  auto-discovers that name at a plugin root, which would install every template into every
  consuming project as a live subagent.

## Evals

`evals/` measures what the skills actually do. The authoring rules in
[Checks](#checks) confirm a skill is well formed; they cannot confirm it changes an agent's
output, or that its `description` routes the right tasks to it. Two measurements cover that:

- **Task evals.** Each skill has 4 to 6 multi-step task prompts in `tasks.json`, each with a
  fixture repository and a set of objective checks in `assertions.json` derived from that
  skill's own Verify and Verification checklist sections. Every task runs twice against an
  identical fixture copy, once with the skill available and once without. The only difference
  between the two runs is a single-skill plugin passed with `--plugin-dir`, so a delta is
  attributable to the skill.
- **Trigger evals.** `trigger-eval.json` holds 10 routing probes per skill, five in scope and
  five adjacent but out of scope, which measure the `description` field rather than the body.

```sh
python3 evals/run_eval.py tasks    --skill <name> --model sonnet --parallel 5
python3 evals/run_eval.py triggers --skill <name> --model sonnet --parallel 5
python3 evals/run_eval.py report   --skill <name>
```

Results land in `evals/<skill>/results/<date>.md`, rendered by `report` rather than written by
hand, with transcripts, workspaces, and per-run grades kept under `results/raw/<date>/`. A
delta of zero is reported as a delta of zero: where a skill produces no measurable
improvement, the results file says so. See [evals/README.md](evals/README.md) for how the two
conditions are isolated, what an assertion may and may not be, and the limitations that apply
to every number in there.

Every skill defines both evals, and all six have results committed. The table records the
latest stamp for each skill, what it measured, and the limitation that keeps that number from
standing as a general claim about the skill.

| Skill | Latest stamp | Task delta | Cost | Routing | Limitation |
| --- | --- | --- | --- | --- | --- |
| `ansible-verification-loop` | 2026-07-28-isolation | +1 over 1 task | 1.8x | 10/10 (2026-07-25) | One task, one run per condition. The broader stamp, 2026-07-25, measured +6 over 5 tasks at 2.2x, with `avl-05` classified truncated rather than graded. |
| `bash-secure-scripting` | 2026-08-14 | +9 over 4 tasks | 3.5x | 9/10 | One run per condition, so variance is uncontrolled. `bss-t09` is out of scope and routed in. |
| `bash-testing` | 2026-08-14 | +1 over 4 tasks | 2.1x | 7/10 | Two fixtures pass fully in both conditions and cannot discriminate. `bt-t01` and `bt-t04` are in scope and never routed; `bt-t07` is out of scope and routed in 2 of 3 repetitions. |
| `github-actions-security` | 2026-07-27 | +21 over 3 tasks (2026-07-25) | 2.6x | 9/10 | The latest stamp graded no tasks. `gas-t06` is out of scope and routed in on all 3 repetitions. |
| `python-secure-coding` | 2026-07-28, marked for regeneration | +4 over 5 tasks | 1.7x | 10/10 (2026-07-25) | Only `psc-02` has a delta not marked *no reliable difference*, and on `psc-03`, `psc-04` and `psc-05` the with-skill condition failed the same security assertions as the baseline. The fixtures were anchored for `ty` on 2026-08-17, which this stamp predates; see [evals/python-secure-coding/README.md](evals/python-secure-coding/README.md). |
| `python-testing` | 2026-07-28 | +1 over 5 tasks | 1.4x | 9/10 (2026-07-25) | Four of five deltas are zero or marked *no reliable difference*, at $2.07 per net assertion gained. |

Two limits cut across the whole table. A routing score carried from an earlier stamp than the
task result was measured against an earlier revision of that skill's `description`, so it does
not transfer forward on its own. And a task delta is a measurement of the skill revision that
ran, not of the file as it stands now: editing a skill, its `tasks.json` or its
`assertions.json` invalidates the stamp above it until the eval is run again.

Eval fixtures are deliberately flawed inputs, so `pyproject.toml` excludes
`evals/*/fixtures`, `evals/*/results`, and `evals/probe-sandbox` from `ruff` and `ty`. Each
fixture carries its own tool configuration, which is what the eval measures against.
Markdown is the exception: `.markdownlint-cli2.yaml` ignores only `evals/*/results/raw/**`,
the verbatim transcripts and workspaces of a graded run, so a fixture's own `README.md` is
still held to this repository's Markdown rules.

## Checks

`.github/workflows/lint.yml` enforces the rules above on every push and pull request, in four
jobs: the authoring rules, this repository's own Python, its own workflows, and its Markdown.
Every check runs locally:

```sh
uv run --frozen python scripts/check_skills.py   # authoring rules for every SKILL.md
uv run --frozen ruff check .                     # the repository's own Python
uv run --frozen ruff format --check .
uv run --frozen ty check .
npx --yes markdownlint-cli2@0.23.2 "**/*.md"     # add --fix to correct spacing in place
docker run --rm -v "$PWD:/repo" -w /repo rhysd/actionlint:1.7.12 -color
uvx zizmor@1.29.0 --persona=pedantic --no-progress .github/
```

The last two are this repository's own workflows held to the skill it publishes about them,
at the versions `skills/github/github-actions-security/SKILL.md` pins in its Verify section.
`zizmor` is scoped to `.github/` for the same reason `ruff` excludes `evals/*/fixtures`: a
fixture workflow plants the finding its eval measures.

`scripts/check_skills.py` verifies, for each `skills/*/*/SKILL.md`, that the frontmatter parses as
YAML, `name` matches the parent directory, `description` is non-empty, under 1,024 characters, and
not written in first or second person, that the body is under 500 lines, and that the body carries
the bounded verify loop in the shared wording described above. It applies the same
frontmatter rules to each `agent-templates/*.md`, with `name` matching the file name, and adds the
neutral defaults a template must ship with: `model` is `inherit` and `tools` is a non-empty
allowlist. It then checks `.claude-plugin/marketplace.json`: it must parse, every listed path must
hold a `SKILL.md`, and every skill in the repository must be listed by exactly one plugin. It fails
if an `agents/` directory has appeared at the repository root, which would ship the agent templates
as installable subagents. It verifies the cross-references this library maintains by hand: a
`SKILL.md` may not name an `instructions/*.md` that does not exist, an `instructions/*.md` may not
name a `skills/*/*/SKILL.md` that does not exist, and a skill that names an instructions document
must be named back by it, which is the bidirectional rule stated above. It requires every
`references/*.md` over 100 lines to carry a `## Contents` section ahead of every other section, and
compares its entries against the headings that follow, so a list cannot drift into pointing at a
section that has been renamed or removed. Last, it holds the prose
this repository writes about itself, meaning `README.md`, `instructions/*.md`, `skills/**/*.md`,
`agent-templates/*.md`, and the hand-written `evals/*/README.md`, to the em dash, arrow,
inflated-vocabulary, and grammatical-person rules in
`instructions/written_language_instructions.md`. Fenced blocks, inline code spans, and table rows
are exempt, because the rule allows those and a document has to be able to quote what it bans. The
person check additionally exempts Markdown link text and double-quoted spans, which is where a
cited title and a quoted example live. The word list carries only the entries with no technical
meaning in this subject matter: `harness` and `elevate` stay legal, since "test harness" and
"privilege elevation" are the domain's own terms. It needs only `pyyaml`, so
`python3 scripts/check_skills.py` also works outside uv.

`claude plugin validate .` checks the marketplace manifest against Claude Code's own schema. It
needs the Claude Code CLI, so it is a local step rather than a CI one.

Markdown rules apply to every `.md` file and are configured in `.markdownlint-cli2.yaml`: prose
wraps at 100 columns, headings and lists are surrounded by blank lines, and code fences declare a
language. The `ruff` and `ty` steps hold this repository's own Python to
`instructions/python_coding_instructions.md`, with the tool versions pinned in `uv.lock` and every
lint ignore justified in `pyproject.toml`.
