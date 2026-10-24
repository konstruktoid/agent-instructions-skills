# A run's process cleanup killed itself and a sibling run

## Evidence

In the 2026-10-24 stamp, two of the three `with-skill` runs of `bss-03-provision-user` exited
with return code 143, SIGTERM, without a result event, and were recorded as aborted. Run 1 started
at 13:19:54 UTC and ran 172.9 s, run 2 started at 13:19:55 and ran 171.9 s, so both ended at
13:22:47, within 0.1 s of each other. Run 3 started at 13:19:58 and exited normally after 66.6 s.
The suite ran with `--parallel 5`, so all three ran in one process namespace on one machine.

- `evals/bash-secure-scripting/results/raw/2026-10-24/bss-03-provision-user/with-skill/run-1/grade.json`
- `evals/bash-secure-scripting/results/raw/2026-10-24/bss-03-provision-user/with-skill/run-2/grade.json`
- `evals/bash-secure-scripting/results/raw/2026-10-24/bss-03-provision-user/with-skill/run-2/run.jsonl`

Run 2 started a test of its edited script that did not finish, then ran `pkill -f provision-user.sh`
(`evals/bash-secure-scripting/results/raw/2026-10-24/bss-03-provision-user/with-skill/run-2/run.jsonl:44`),
and later
`ps -eo pid,args | grep '[p]rovision-user' | awk '{print $1}' | xargs -r kill` (`:50`). Neither
pattern is limited to the run's own workspace or its own processes. The tool result of the last
call in both run 1 and run 2 is `Exit code 137`.

The task's prompt names `sbin/provision-user.sh`, and `claude_command` passes the prompt as an
argument. A probe on 2026-10-24 started `claude -p` with a prompt holding a marker string and
found the whole prompt in the process's `ps -eo pid,args` line, so a pattern that matches the
prompt matches the `claude -p` process of every run of this task.

## Hypotheses

- **Run 2's `kill` at `:50` sent SIGTERM to the `claude -p` process of run 1 and of run 2.**
  Supported: the pattern matches both processes' argument lists, both received SIGTERM, and they
  ended at the same moment. Run 3 had already exited.
- **The `pkill -f provision-user.sh` at `:44` did the same.** Untested. The pattern matches the
  same argument lists, yet run 2 went on to `:50`, which nothing above explains.
- **The skill caused the broad pattern.** Untested. Three runs of one arm cannot separate the
  skill from the model, and no baseline run of this task started a process it had to clean up.

## Reproduction

2 of 3 `with-skill` runs of `bss-03-provision-user` aborted, at `56262a6`, with `--parallel 5`. No
attempt has been made to reproduce it.

## Disposition

open. The 2026-10-24 stamp keeps the aborted runs, so its `bss-03-provision-user` `with-skill`
cell rests on one run rather than three. The cause sits outside what the suite measures: parallel
runs share one process namespace, so one run's agent can signal another run's processes. The next
action is a decision on the harness, a process namespace per run or serial runs for any task whose
fixture starts processes, and then a re-run of the task.
