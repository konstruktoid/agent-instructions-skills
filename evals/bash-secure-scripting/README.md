# bash-secure-scripting evals

Four feature requests, each against a fixture whose script carries the defects the skill covers
on the exact lines the request forces the agent to touch: no strict mode and a predictable
`/tmp/$$` directory that is never cleaned up (`bss-01`), `eval` on a caller-supplied name plus a
Slack payload and an `ssh` command built by string concatenation (`bss-02`), a password generated
from `$RANDOM` and passed to `mysql` in argv, then written to a log (`bss-03`), and a traversal
over `$(ls)` with an unchecked `cd` and an unguarded `rm -rf` (`bss-04`).

No prompt mentions security, hardening, quoting, or ShellCheck. Every one is an ordinary feature
request, so only the skill can surface the rest.

Run it with:

```sh
python3 evals/run_eval.py tasks    --skill bash-secure-scripting --model sonnet --parallel 4
python3 evals/run_eval.py triggers --skill bash-secure-scripting --model sonnet --parallel 5
python3 evals/run_eval.py report   --skill bash-secure-scripting
```

## What the numbers can and cannot show

- `shellcheck` must be on the PATH of whoever runs the eval, or through `EVAL_TOOL_BIN`. Without
  it the `shellcheck-clean` and `verify-clean-or-reported` assertions fail in both arms and measure
  nothing.
- The fixtures ship no `.shellcheckrc`. Default ShellCheck already reports the unquoted
  expansions, so the quoting-adjacent assertions mostly measure whether the agent ran the linter
  at all. The strict-mode, cleanup, validation, environment, and secret assertions are the ones no
  linter answers, and they are where a delta is meaningful.
- `bss-01` and `bss-04` are runnable inside the workspace against their own sample data, so their
  assertion sets include an execution check. `bss-02` and `bss-03` call `ssh`, `curl`, `useradd`,
  and `mysql`, so they are graded statically plus `bash -n`.
- `bss-04` carries a workspace directory whose name contains spaces, which a naive rewrite of the
  `$(ls)` loop still mishandles.

Read the delta column first. A delta of zero means the baseline already handled that task and the
fixture needs a harder defect, not that the skill succeeded.

## Baseline state of the fixtures

Every fixture starts by failing nearly every assertion, which is the headroom the measurement
needs. A reference solution written against `bss-01` passes all of its assertions, so the set is
achievable rather than aspirational.
