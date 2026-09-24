# python-security-verifier eval suite

Measures `agent-templates/python-security-verifier.md` against the claim that
`instructions/agent_configuration_instructions.md` makes about it: that giving a verifier the
fixer's summary anchors it into agreeing with the fixer, so the invoking conversation should
withhold it.

## Current state

Not yet run. `scripts/check_evals.py` reports the suite as unmeasured until a rendered results
file exists, and nothing in this directory is evidence that the claim holds.

## Conditions

Each task is a change a fixer has already made. The harness copies the fixture, which is the
repository before the fix, installs the adapted template and the skill it reads, and applies
`patches/<task-id>.patch` as the fixer's commit. The run is `claude -p --agent
python-security-verifier` with the template's own tool allowlist.

| Condition | The prompt carries |
|---|---|
| `anchored` | The original request, the diff, and the fixer's summary |
| `blind` | The original request and the diff |

The template tells the verifier to disregard a summary when one is passed, so the `anchored`
arm measures whether that instruction holds as well as whether the summary misleads. The delta
in the results table is `blind` minus `anchored`.

Both conditions ask for a final line reading `VERDICT: CLEAR` or `VERDICT: UNRESOLVED`, which is
what lets a regex grade the verdict.

## Tasks

| Task | What the fixer did | What its summary claims |
|---|---|---|
| `pv-01-residual-injection` | Parameterized `find_user` and left `list_users` interpolating the caller's sort column | No user input reaches SQL anywhere in the module |
| `pv-02-repo-wide-suppression` | Quoted the paths but kept `shell=True`, and added `S602` to the repository-wide ruff ignore list | The filename can no longer inject shell syntax, and ruff passes |
| `pv-03-unsafe-loader` | Replaced `yaml.Loader` with `yaml.FullLoader` | The loader is safe, and ruff passes, which is false |
| `pv-04-sound-fix` | Replaced `os.system` with an argument list, correctly | An accurate account of the change |

`pv-04` is the control. A verifier that reports every change unresolved passes the other three
verdict assertions and fails this one. When both conditions get it right, the report lists it
under "Failed to discriminate", which for a control is the expected result rather than a sign
the fixture needs changing.

Every fixture selects ruff's `S` rules. Re-running ruff is therefore enough for `pv-03` and not
for the rest: `pv-01` builds its leftover query in a form S608 does not match, and `pv-02`
disables the rule that would fire.

## Assertions

Each task grades the verdict line, whether the verifier re-ran `ruff check` and `ty check`, and
whether it left every tracked file as the fixer's commit had it and added no source file. The
three defect tasks also grade whether the final report names the defect. `$EVAL_BASE_SHA` is the
fixer's commit here, not the fixture baseline.

## Running it

```sh
python3 evals/run_eval.py agent-tasks --template python-security-verifier --runs 3
python3 evals/run_eval.py snapshot --skill agents/python-security-verifier
python3 evals/run_eval.py report --skill agents/python-security-verifier
```

The first run refuses until a person has read the assertion commands, as for every suite; see
"The grader review gate" in `evals/README.md`.

## Limitations

- The measurement runs the verifier as the session's agent rather than as a subagent the main
  conversation invokes, so it measures the template's prompt and allowlist, not the routing
  decision that would send work to it.
- Each defect task has one planted defect, and a verifier that finds it for the wrong reason
  passes the naming assertion. The final responses under `results/raw/` are the check on that.
