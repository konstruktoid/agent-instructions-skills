# Agent Instructions and Skills

This repository is a library of reusable guidance for AI coding agents. It contains two kinds of
material: instructions documents that describe how output in a given domain should be produced,
and Claude Code skills that describe a repeatable procedure an agent should follow, including
when to follow it and how to verify the result.

## Repository structure

```text
instructions/     Domain-specific writing and coding standards (plain Markdown, no frontmatter)
skills/           Claude Code skills, one directory per skill: skills/<category>/<name>/SKILL.md
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
| `github-actions-security` | `skills/github/github-actions-security/SKILL.md` | Authoring and reviewing GitHub Actions workflows and actions: least-privilege `GITHUB_TOKEN` permissions, dependencies pinned by commit SHA to the latest published release, injection-safe handling of untrusted event data, safe triggers and runners, and structures that scale across repositories, run through a bounded verify-fix loop with `actionlint` and `zizmor`. |
| `python-secure-coding` | `skills/python/python-secure-coding/SKILL.md` | The `ruff`/`ty` baseline from `python_coding_instructions.md`, extended with Python-specific security best practices aligned to the OWASP Top 10:2025 (input handling, deserialization, secrets, subprocess/SQL/crypto usage, SSRF, dependency hygiene), run through a bounded verify-fix loop. |
| `python-testing` | `skills/python/python-testing/SKILL.md` | Adding or updating pytest coverage for a Python change: discovering and matching the repository's existing test layout, deciding when a test is required, and running the suite through a bounded verify-fix loop. |

## Using this library from another project

A consuming project should not copy these files or write its own version of them. Use one of the
mechanisms below, each of which keeps a single upstream copy that can be updated in place.

### Skills, as a Claude Code plugin

This repository is its own plugin marketplace. The skills are grouped into three plugins so a
project installs only what it needs:

| Plugin | Skills |
|--------|--------|
| `python-standards` | `python-secure-coding`, `python-testing` |
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

### Copying, as a last resort

Copy a file only when the consuming environment can use neither a plugin nor a submodule, such as
an air-gapped checkout. Record the upstream commit the copy came from, so the drift is visible
later. A copy stops receiving fixes the moment it is made, which is the outcome the mechanisms
above exist to avoid.

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
- For any skill with a verify-then-fix cycle, bound the retries explicitly and define what one
  attempt is: one full fix-and-rerun cycle. This repo baselines the bound at 3 attempts, lets an
  agent continue while each cycle produces strictly fewer findings, and requires it to stop early
  when the loop oscillates without progress. On stopping, the skill must require reporting the
  failing check and its output to the user, instead of looping silently or declaring success
  unverified. All three skills use the same wording for this loop; copy it rather than
  paraphrasing, so the bound means the same thing everywhere.
- When a skill extends or depends on an instructions document, cross-reference it by path in both
  directions, as done between `python_coding_instructions.md` and `python-secure-coding`. Do not
  copy the shared material into both files. The instructions document is the single source of
  truth; the skill carries a short summary and a pointer to it.

## Checks

`.github/workflows/lint.yml` enforces the rules above on every push and pull request. Every check
runs locally:

```sh
uv run --frozen python scripts/check_skills.py   # authoring rules for every SKILL.md
uv run --frozen ruff check .                     # the repository's own Python
uv run --frozen ruff format --check .
uv run --frozen ty check .
npx --yes markdownlint-cli2@0.23.1 "**/*.md"     # add --fix to correct spacing in place
```

`scripts/check_skills.py` verifies, for each `skills/*/*/SKILL.md`, that the frontmatter parses as
YAML, `name` matches the parent directory, `description` is non-empty, under 1,024 characters, and
not written in first or second person, and that the body is under 500 lines. It then checks
`.claude-plugin/marketplace.json`: it must parse, every listed path must hold a `SKILL.md`, and
every skill in the repository must be listed by exactly one plugin. It needs only `pyyaml`, so
`python3 scripts/check_skills.py` also works outside uv.

`claude plugin validate .` checks the marketplace manifest against Claude Code's own schema. It
needs the Claude Code CLI, so it is a local step rather than a CI one.

Markdown rules apply to every `.md` file and are configured in `.markdownlint-cli2.yaml`: prose
wraps at 100 columns, headings and lists are surrounded by blank lines, and code fences declare a
language. The `ruff` and `ty` steps hold this repository's own Python to
`instructions/python_coding_instructions.md`, with the tool versions pinned in `uv.lock` and every
lint ignore justified in `pyproject.toml`.
