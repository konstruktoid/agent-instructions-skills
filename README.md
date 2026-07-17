# Agent Instructions and Skills

This repository is a library of reusable guidance for AI coding agents. It contains two kinds of
material: instructions documents that describe how output in a given domain should be produced,
and Claude Code skills that describe a repeatable procedure an agent should follow, including
when to follow it and how to verify the result.

## Repository structure

```
instructions/   Domain-specific writing and coding standards (plain Markdown, no frontmatter)
skills/         Claude Code skills, one directory per skill: skills/<category>/<name>/SKILL.md
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
sections such as Purpose, When to use this, When NOT to use this, Steps, Verify, and Verification
checklist. The `description` field is what a Claude Code agent uses to decide whether a skill
applies to the current task, so it should state concretely what the skill is for and when it
should trigger.

To make a skill in this repository available to Claude Code, either:

- Copy or symlink the skill's directory into the target project's `.claude/skills/` directory.

Once available, a skill is invoked automatically when its `description` matches the current task,
or explicitly through the Skill tool or a slash command named after it.

Current skills:

| Skill | Path | Covers |
|-------|------|--------|
| `ansible-verification-loop` | `skills/ansible/ansible-verification-loop/SKILL.md` | Reviewing or modifying Ansible roles and collections, verified through the repository's own lint/test loop. |
| `python-secure-coding` | `skills/python/python-secure-coding/SKILL.md` | The `ruff`/`ty` baseline from `python_coding_instructions.md`, extended with Python-specific security best practices (input handling, deserialization, secrets, subprocess/SQL/crypto usage, dependency hygiene). |

## Adding new material

- Add a new instructions document to `instructions/` when the goal is a style or quality standard
  for a category of output. Follow the existing files' structure: Objective, required/avoid style
  rules, and a Quality Checklist.
- Add a new skill to `skills/<category>/<name>/SKILL.md` when the goal is a repeatable procedure
  with a verification step. Follow the existing skills' structure, and write the `description`
  field so it states precisely which tasks should trigger the skill.
- When a skill extends or depends on an instructions document, cross-reference it by path in both
  directions, as done between `python_coding_instructions.md` and `python-secure-coding`.
