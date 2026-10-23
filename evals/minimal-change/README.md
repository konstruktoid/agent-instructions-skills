# minimal-change evals

Six tasks that measure `instructions/minimal_change_instructions.md` in three arms on identical
fixtures: `baseline` (no instruction), `doc` (the document, referenced from a project
`CLAUDE.md`), and `plain` (one sentence asking for the smallest complete change). The question
is whether the document keeps correctness while producing less code than the plain sentence
does. A document that does not beat a sentence is not worth its length.

Every task offers a tempting overbuild, and every assertion grades whether a smaller change
stayed correct. Size is never asserted. The harness records lines added, lines deleted, and
output tokens for each run, and the report sets them beside the correctness tally.

| Task | The overbuild on offer | What the assertions check |
|---|---|---|
| `mc-01-reuse-slugify` | A hand-rolled slug function | The fixture's `slugify` is called, and an accented title comes out right. |
| `mc-02-parse-when` | A date library for ISO 8601 text | No new import or manifest change, garbage rejected, and a test added. |
| `mc-03-export-rows` | Delimiter and encoding options | The function takes exactly the two requested parameters, and commas and quotes round-trip. |
| `mc-04-set-quantity` | None. Copying the house style cuts validation | Seven malformed requests raise `ValueError` and leave the cart unchanged. |
| `mc-05-save-settings` | A second temp-file-and-rename routine | The fixture's `atomic_write` is called, and a failed save keeps the old file. |
| `mc-06-audit-controls` | None. Two controls look redundant | All five controls in `POLICY.md` are checked, each by its own assertion. |

`mc-04` and `mc-05` are the never-cut tasks, where the smaller answer is the wrong one.
`mc-06` is the scope carve-out, where `POLICY.md` is the scope and the defaults that already
satisfy three controls do not remove them.

The fixtures use only the standard library, so any third-party import counts as a new
dependency. The assertions were checked before any paid run against a correct small solution,
which passes all of them, and against the failure each task is built to catch: a hand-rolled
slug, a date library, an extra option, a validator copied from the house style, a direct write,
and a check that stops at two controls. Each failure is caught by the assertion meant for it.

Run it from a checkout outside the home directory, so that no ancestor `CLAUDE.md` reaches the
baseline:

```sh
python3 evals/run_eval.py instructions-tasks --suite minimal-change --runs 3 --parallel 5
python3 evals/run_eval.py report --skill minimal-change
```

## Limits

- Six tasks in one language and one model tier cannot support a claim about every repository.
- Assertions grade correctness only where a hidden check can see it. A change that is smaller
  because it dropped something no assertion probes scores as correct.
- Test-writing and output tokens varied a great deal between draws: an earlier run of this suite,
  on an uncommitted tree, had the baseline write tests and the document use fewer tokens than
  the baseline. Three runs per arm do not settle either.
- The 2026-10-20 `baseline` had this repository's `AGENTS.md` loaded as instructions, through
  Claude Code's builtin AGENTS.md plugin, so it was not an agent without instruction. The `doc`
  and `plain` arms were not exposed. See `incidents/baseline-reads-checkout.md`.
- The `doc` arm gives the agent a pointer rather than the text, so a run that never opens the
  document measures the pointer. The report counts those runs.
