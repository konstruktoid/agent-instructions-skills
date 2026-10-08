# requirements-analyst eval suite

Measures `agent-templates/requirements-analyst.md` against the claim its description makes: that
an analysis before implementation surfaces the contradictions and decisions a plain reading of an
ambiguous request misses, without inventing questions for a request that has none.

## Current state

Never run. `scripts/check_evals.py` reports the suite as unmeasured. Nothing here is a result.

Four tasks with three runs per condition detect only a large effect. If a run is made and the
conditions score alike, the finding is "no detectable effect", not "no effect".

## Conditions

The comparison is `template-vs-no-agent`, the only one the suite declares. Each task is a coding
request that has not been acted on, against a fixture repository. Both conditions get the same
prompt: an introduction asking for an analysis and no file changes, the request, and a request
for a final `OPEN-DECISIONS: <n>` line, which is what lets a regex grade the count.

| Condition | The run |
|---|---|
| `no-agent` | `claude -p` with the harness's `TASK_TOOLS` allowlist and no agent installed |
| `agent` | `claude -p --agent requirements-analyst` with the adapted template installed, and the template's own `Read, Grep, Glob` allowlist |

The delta in the results table is `agent` minus `no-agent`. The two conditions differ in the role
text, the reasoning discipline and the tool allowlist, so a difference cannot be attributed to
any one of them. The control can edit files and the treatment cannot, so the no-edit assertions
can fail the control for a reason the template removes by construction. To isolate the
reasoning-discipline section instead, declare `discipline-ablation` in `tasks.json` and run
`--comparison discipline-ablation`; the harness supports it for any template that has the
section.

The template reads `<submodule>/instructions/written_language_instructions.md`. The harness
installs the library's `instructions/` directory at `.agent-standards/` in the workspace and
substitutes that path, as README.md tells a consuming project to for a submodule install.

## Tasks

| Task | Fixture plants | Request |
|---|---|---|
| `ra-01-unit-conflict` | `README.md` documents `--timeout` in seconds, and `src/fetchkit/config.py` reads `TIMEOUT_MS` in milliseconds | Make the timeout configurable and keep existing behaviour |
| `ra-02-public-rename` | `fetch` is re-exported in `__init__.py` and marked stable in `docs/api.md` | Rename `fetch` to `fetch_user` |
| `ra-03-control` | Nothing: the flag, its output, its exit status and its test location are specified | Add `--version` printing `__version__`, with a test beside the existing ones |
| `ra-04-entry-point` | `legacy_export` has no caller in the Python sources, and `pyproject.toml` registers it in the public `reportkit.exporters` entry-point group | Delete the unused `legacy_export` function |

`ra-03-control` is the control. An analyst that always invents a question fails its
`OPEN-DECISIONS: 0` assertion. When both conditions get it right, the report lists it under
"Failed to discriminate", which for a control is the expected result.

## Assertions

`ra-01`, `ra-02` and `ra-04` grade a nonzero `OPEN-DECISIONS` count and a report that names the
planted conflict: both units for `ra-01`, `__init__` or `api.md` for `ra-02`, and the entry point or
`pyproject` for `ra-04`. `ra-01` matches `\bseconds?\b` rather than `second`, because `milliseconds`
contains `seconds`. `ra-03` grades `OPEN-DECISIONS: 0` and that the report names `__version__`.
Every task grades that no tracked file changed and no source, configuration or Markdown file was
added. `$EVAL_BASE_SHA` is the workspace as the run started. No assertion asks for a judgment.

## Running it

```sh
python3 evals/run_eval.py agent-tasks --template requirements-analyst --runs 3
python3 evals/run_eval.py snapshot --skill agents/requirements-analyst
python3 evals/run_eval.py report --skill agents/requirements-analyst
```

The first run refuses until a person has read the assertion commands, as for every suite; see
"The grader review gate" in `evals/README.md`.

## Limitations

- The measurement runs the template as the session's agent rather than as a subagent the main
  conversation invokes, so it measures the template's prompt and allowlist, not the routing
  decision that would send work to it.
- The count is the analyst's own and a regex checks only whether it is zero. Three planted
  conflicts are checked by name, so a report that names them for the wrong reason passes. The
  final responses under `results/raw/` are the check on that.
- The fixtures are small and the planted conflict sits in files the request names or one hop
  from them, so a thorough reader finds it. Expect a ceiling.
