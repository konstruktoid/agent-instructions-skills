# Should `instructions/` collapse into skill `references/` directories?

Report only. Nothing in this document has been applied.

## The question

`instructions/` and `skills/` are separate trees, joined by cross-references maintained by
hand in both directions, as between `instructions/python_coding_instructions.md` and
`skills/python/python-secure-coding/SKILL.md`. The proposal is to move each instruction
document into a `references/` directory inside the skill that depends on it, so a skill
carries its own material and the progressive-disclosure pattern runs metadata to SKILL.md
body to bundled references without leaving the skill directory.

## Recommendation

**Do not collapse `instructions/` into skill `references/` directories.** Keep the current
split and remove the maintenance burden mechanically instead, by extending
`scripts/check_skills.py` to verify the cross-references rather than trusting them.

Two findings drive this.

### The mechanism being "fixed" is already working

The eval runs record which files each agent read. Across the with-skill runs of this
library's own evals:

- 9 runs read `instructions/python_coding_instructions.md` through
  `${CLAUDE_PLUGIN_ROOT}/instructions/`. No baseline run read it, which is expected: without
  the skill there is no pointer to follow.
- `references/` files were loaded selectively, matching the triage table rather than
  wholesale: `injection.md` on the SQL and subprocess tasks, `deserialization.md` on the
  pickle task, `secrets.md` on the credential tasks, `access-control.md` on the SSRF task,
  and `yaml-quoting.md` on the YAML quoting task.

Evidence: `evals/*/results/raw/*/*/with-skill/run.jsonl`.

Progressive disclosure is a property of when material is loaded, not of where it sits on
disk. Both levels already load on demand and only when they apply. A directory move would
not change what any agent reads, so it buys no behavioural improvement, and these runs are
the evidence that the cross-directory path resolves correctly under a real plugin install.

### Every instruction document has more than one consumer

Collapsing assumes a document belongs to one skill. None currently does:

| Document | Consumers |
|---|---|
| `python_coding_instructions.md` | `python-secure-coding`, `python-testing`, and any project referencing it from `CLAUDE.md` |
| `written_language_instructions.md` | `github-actions-security`, `overview_document_instructions.md`, the `prose-editor` agent template, and any project applying a prose style to all output |
| `overview_document_instructions.md` | No skill. It is a standalone document. |

Moving `python_coding_instructions.md` into `python-secure-coding/references/` forces one of
three outcomes, each worse than the status quo: `python-testing` reaches across a sibling
skill's directory, the file is duplicated (which the repository's own rule in
[README.md](../README.md) forbids, since the instructions document is the single source of
truth), or the two Python skills merge. `written_language_instructions.md` is worse still,
because two of its four consumers are not skills at all, and the submodule workflow exists
specifically so a project can reference it directly from `CLAUDE.md`.

`overview_document_instructions.md` has no skill to collapse into.

## What to do about the real problem

The cross-references are the genuine complaint: they are prose in two files that can drift
apart silently. That is a checking problem, not a layout problem. `scripts/check_skills.py`
already enforces the repository's other authoring rules and is the natural place for it:

1. For each `skills/*/*/SKILL.md`, extract every `instructions/*.md` path it mentions and
   fail when the file does not exist.
2. For each `instructions/*.md`, extract every `skills/*/*/SKILL.md` path it mentions and
   fail when that skill does not exist.
3. Fail when a skill names an instructions document that does not name it back, so the
   bidirectional rule stated in `README.md` is enforced rather than assumed.

This is roughly 40 lines in the existing style, costs one CI step, and removes the drift risk
without moving a file or breaking the submodule and plugin install paths.

## Migration steps, if the decision goes the other way

Recorded for completeness. These assume the trade-offs above are accepted.

1. Decide an owner skill per document. `python_coding_instructions.md` has no single owner
   today, so either merge `python-secure-coding` and `python-testing` into one skill, or
   accept that one reaches into the other's `references/`.
2. `git mv instructions/<doc>.md skills/<category>/<owner>/references/<doc>.md`, preserving
   history.
3. Rewrite every link. In the owner skill, `instructions/<doc>.md` becomes
   `references/<doc>.md`. In non-owner skills it becomes a relative path across skill
   directories, which no existing skill does today.
4. Delete the reverse cross-reference sections from the moved documents, since a reference
   file inside a skill has no reason to point back at its own SKILL.md.
5. Update `README.md`: remove the `instructions/` row from the repository structure table,
   remove the "Instructions documents, and non-plugin setups" section, and rewrite the
   "Adding new material" rule that requires bidirectional cross-referencing.
6. Update `agent-templates/prose-editor.md`, which references
   `instructions/written_language_instructions.md` by path and has no skill namespace to
   fall back on. Under a plugin install it would need the owner skill preloaded through the
   `skills:` frontmatter field instead.
7. Find a home for `overview_document_instructions.md`, which no skill consumes. Either
   leave `instructions/` in place for it alone, which defeats the purpose, or create a skill
   to own it.
8. Announce the break. Any consuming project that references
   `.agent-standards/instructions/*.md` from its `CLAUDE.md`, which is the documented
   submodule workflow, has its paths broken by the move.
9. Re-run the evals and confirm the reference-loading pattern above is unchanged. The runs
   in `evals/*/results/raw/` are the before-picture to compare against.

Step 8 is the one to weigh hardest: it is a breaking change to the library's public surface
in exchange for no measured behavioural gain.
