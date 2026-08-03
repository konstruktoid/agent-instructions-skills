# bash-testing evals

Four changes to shell scripts, each in a repository with a different existing test convention,
because the skill's first claim is that it discovers and matches what is already there:

| Task | Existing convention | The change |
|---|---|---|
| `bt-01-plain-suite` | Plain `test/test_*.sh` scripts, a shared `helpers.sh`, a `run-tests.sh` runner | Fix `--exclude=PATTERN`, which is silently dropped |
| `bt-02-bats-suite` | bats-core, `test/*.bats` with a `test_helper.bash` | Add a `--json` output mode, keeping the text output identical |
| `bt-03-inline-script` | `*_test.sh` files next to the code they cover | Reject an empty `--name` in a script with no functions |
| `bt-04-no-suite` | None at all | Make a cron script fail on a missing directory |

`bt-01` and `bt-03` carry a real defect the new coverage has to pin, and both are graded on the
behavior as well as on the test file, so a run that writes a test but breaks the script cannot
pass on test files alone. `bt-03` also measures whether the script is made testable: the skill
asks for logic in functions behind a `BASH_SOURCE` guard rather than a rewrite.

`bt-04` has no suite and no framework, which is the case the skill handles with a rule rather than
a test: state the coverage decision, and verify by running the script directly including the
failure path.

Run it with:

```sh
python3 evals/run_eval.py tasks    --skill bash-testing --model sonnet --parallel 4
python3 evals/run_eval.py triggers --skill bash-testing --model sonnet --parallel 5
python3 evals/run_eval.py report   --skill bash-testing
```

## What the numbers can and cannot show

- Every fixture starts shellcheck-clean with a passing suite, so anything failing afterwards is
  attributable to the change rather than to the starting state.
- `bats` is not assumed to be installed. `bt-02`'s suite assertion exits 0 when `bats` is absent,
  so it never fails for a reason the run had no control over. Provision it through
  `EVAL_TOOL_BIN` to make that assertion a real check.
- `shellcheck` and `make` must be available to the grader, as must `python3`, which `bt-02` uses
  to confirm the JSON output parses.
- The "no second framework" assertions are the ones most likely to separate the arms, because
  introducing bats into a repository that tests with plain scripts is the failure the skill exists
  to prevent.

Read the delta column first. A delta of zero means the baseline already handled that task and the
fixture needs a harder starting point, not that the skill succeeded.
