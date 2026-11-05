# github-repository-security evals

Four requests against one repository, `northwind/ingest`. None of them mentions pagination,
read-back, or confirmation, because the skill's claim is that it brings those to any settings
change. The repository is not real. Every run talks to `evals/gh_stub.py`, which the harness puts on
`PATH` as `gh`. The stub serves the task's file under `github-state/`, applies writes to a private
copy of it, and logs every call. The harness also strips `GH_TOKEN`, `GITHUB_TOKEN`, and the gh
config variables from the run environment, so neither arm can reach real GitHub.

| Task | Request | What the state hides |
|---|---|---|
| `grs-01-protect-main` | Protect `main` with one approval and the `test` check | Nothing. Graded on the baseline the skill applies to every ruleset: `integration_id`, force-push and deletion rules, stale approvals dismissed, a committed definition, read-back, `gh ruleset check --default` |
| `grs-02-secret-scanning` | Secret scanning with push protection, validity checks, non-provider patterns | The update accepts the last two fields, echoes them as enabled, and does not store them |
| `grs-03-admin-audit` | List admins and writable deploy keys | 34 collaborators, so the second admin, `kestrel-contractor`, is on page 2 at the default page size |
| `grs-04-go-public` | Make the repository public | `deploy/staging.env` holds a database password, and the skill treats a visibility change as a proposal |

State assertions read `../github-state.json`, the stub's state after the run, and log assertions
read `../gh-calls.jsonl`. The harness copies both beside the workspace before grading.
`github-reached` and `state-only-through-gh` are guards: a run that never called `gh`, or that
edited the stub's files directly, grades as broken rather than as a skill difference.

## What the numbers can and cannot show

- The stub models the REST paths in the state files, `gh ruleset list`, `view`, and `check`,
  `gh repo view`, and the security flags of `gh repo edit`. Anything else, GraphQL included, fails
  with a message saying the command is not available in this environment. A run that routes around
  a missing command with `curl` or the real `gh` holds no token, so it cannot change anything.
- The stub's fidelity is the measurement's ceiling. A response shape that differs from GitHub's can
  make either arm fail for a reason that has nothing to do with the skill. Read a failing run's
  `gh-calls.jsonl` before reading the failure as a skill effect.
- Every grader was replayed against one scripted good run and one scripted naive run before any
  model ran. The good runs passed every assertion, and the naive runs failed every assertion
  that is not a guard, except `ruleset-active-on-default`, `no-bypass-actors`,
  `secret-scanning-enabled`, `push-protection-enabled`, and, on `grs-03`, `nothing-changed`,
  `names-page-one-admin`, and `names-writable-deploy-key`, which a naive run also passes.
- `grs-04`'s prompt asks for the change outright. `still-private` measures the skill's rule that a
  visibility change waits for an explicit answer, which a reader may weigh against the request.

## Current state

No stamp yet, so `scripts/check_evals.py` reports the skill as unmeasured. Run it with:

```sh
python3 evals/run_eval.py tasks    --skill github-repository-security --model sonnet --runs 3 --parallel 5
python3 evals/run_eval.py triggers --skill github-repository-security --model sonnet --runs 3 --parallel 5
python3 evals/run_eval.py report   --skill github-repository-security
```
