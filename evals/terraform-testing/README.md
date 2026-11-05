# terraform-testing evals

Two measurements: five routing probes in each direction, and five task prompts that each start from
a different test setup, because the skill's first claim is that it discovers what a repository
already does and matches it.

| Task | Existing setup | The change |
|---|---|---|
| `tt-01-native-suite` | Native tests split into `tests/unit/` (plan only) and `tests/integration/` (apply) | Reject `retention_days` outside 1 to 365 |
| `tt-02-terratest-suite` | Terratest: `test/unit/` plans, `test/integration/` applies | Fix an `endpoint` output that renders `host/port` |
| `tt-03-conditional-resource` | None; `required_version` is 1.7 or later | Add an optional resource behind a boolean, and an output reporting it |
| `tt-04-pinned-old-terraform` | None; CI runs Terraform 1.5.7 and only `make check` | Add an output and keep it covered |
| `tt-05-docs-only` | Native tests | Reword variable descriptions and fix README typos |

`tt-03` is the case where the skill prefers native `terraform test`. `tt-04` is the case where it
must not, because native tests need 1.6, so the pass is a plan-and-policy check or Terratest and an
explanation, and it must run from `make check`, since that is all CI runs. `tt-05` has no behavior
change, which the skill handles with a rule rather than a test: say a test is not needed, and why.

The probe set is five in scope and five out of scope. The in-scope probes are a test for a new
variable validation, a regression test for an output bug, placing a test in an unfamiliar
repository, covering a conditional resource, and extending an existing Terratest suite. The
out-of-scope probes are two for `terraform-secure-iac` (a remote backend and an unpinned module
source), one formatting, one Python test, and one explanation that needs no code.

The first trigger run, stamp `2026-11-04` at `4d9fe5a` on `sonnet` with three passes per probe,
routed 10 of 10 probes correctly. `tt-t08`, the README formatting probe, fired in one of its three
passes, so it is the probe nearest to misrouting. The task suite ran in the
same stamp, `2026-11-05` at `966b828`, and the skill scored 7 assertions better over the five tasks
at 1.4x the cost. `tt-03` (+4) and `tt-04` (+1) separate. `tt-01` scores full marks in both arms,
`tt-02` and `tt-05` are marked no reliable difference, and the skill did not fire on `tt-05`, so
that delta is not attributable to it.

Run it with:

```sh
python3 evals/run_eval.py tasks    --skill terraform-testing --model sonnet --parallel 4
python3 evals/run_eval.py triggers --skill terraform-testing --model sonnet --parallel 5
python3 evals/run_eval.py report   --skill terraform-testing
```

## What the numbers can and cannot show

- Every fixture builds only `terraform_data`, which the built-in provider supplies, so `init`,
  `plan`, `apply` and `test` need no registry access and no credentials. `terraform` must be on the
  PATH of whoever runs the eval.
- Every fixture starts `fmt`-clean with passing checks, so a failure afterwards is attributable to
  the run. A reference solution written against each fixture passes every assertion, and the
  unchanged fixture fails the ones that measure the change.
- `tt-02` is Terratest, and no grader runs `go test`, since each graded run would download Terratest.
  The fixture ships a `test/go.mod` and no `go.sum`, so an agent has to run `go mod tidy` itself.
  The reference test was run with Go 1.27.3: it fails against the buggy module and passes against
  the fixed one. The assertions read the test files and the module, and `gofmt-clean` exits 0 when
  `gofmt` is absent. `suite-actually-run` measures that the agent tried, not that the suite passed.
- The first run, stamp `2026-11-05` at `5e0ec83`, found `tt-01` and `tt-04` at full marks in both
  arms and a `tt-02` prompt and a `tt-05` pattern that mismeasured. The second run left `tt-02` at
  full marks in both arms. The stamp kept is a later run, after those fixes. `tt-01` and `tt-02`
  hide their convention in a unit and integration split, and `tt-04` requires the check to fail
  when the output is wrong.
- `check-fails-when-output-is-wrong` rewrites the value line of the `full_name` output and expects
  `make check` to fail. It assumes the value sits on one line.
- `test-fails-without-the-validation` restores `variables.tf` from the base commit and expects
  `terraform test` to fail. It assumes the `validation` block sits where the variable is declared.
- `suite-passes` on `tt-03` passes on the unchanged fixture, since `terraform test` with no tests
  exits 0. `native-test-added` is the assertion that separates the arms there.
- Graders that run `terraform` do so in a scratch copy named `eval-check`, so grading leaves no
  `.terraform` directory in the workspace. `no-state-plan-or-cache-left` therefore measures what
  the run left, not what grading did.

Read the delta column first. A delta of zero means the baseline already handled that task and the
fixture needs a harder starting point, not that the skill succeeded.
