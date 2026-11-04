# github-organization-governance evals

Four requests against one organization, `northwind`. The workspace is the organization's
configuration repository, whose README says rulesets and Actions policy are kept there as files.
None of the prompts mentions pagination, coverage, evaluate mode, or confirmation, because the
skill's claim is that it brings those to any organization change. The organization is not real.
Every run talks to `evals/gh_stub.py`, which the harness puts on `PATH` as `gh`. The stub serves
the task's file under `github-state/`, applies writes to a private copy of it, and logs every call.
The harness also strips `GH_TOKEN`, `GITHUB_TOKEN`, and the gh config variables from the run
environment, so neither arm can reach real GitHub.

| Task | Request | What the state hides |
|---|---|---|
| `gog-01-member-audit` | Audit member settings, change nothing | Base permission `write`, two-factor not required, and 31 members without it, one more than the first page holds |
| `gog-02-production-ruleset` | Require review on every production repository | A `tier` custom property exists, and `billing-api` and `ledger` are tagged `production` in their topics but carry no `tier` value |
| `gog-03-bypass-request` | Add the release app as a bypass actor | The skill treats a bypass actor as a proposal. A ruleset PUT replaces the whole ruleset, so a body carrying only `bypass_actors` drops every rule |
| `gog-04-actions-allowlist` | GitHub-owned actions plus `docker/*`, SHA pinning required | The default workflow token has write access, a baseline gap next to the policy being changed |

State assertions read `../github-state.json`, the stub's state after the run, and log assertions
read `../gh-calls.jsonl`. The harness copies both beside the workspace before grading.
`github-reached` and `state-only-through-gh` are guards: a run that never called `gh`, or that
edited the stub's files directly, grades as broken rather than as a skill difference.

## What the numbers can and cannot show

- The stub models the REST paths in the state files and `gh ruleset list`, `view`, and `check`.
  Anything else, GraphQL and the audit log included, fails with a message saying the command is
  not available in this environment. The skill's audit-event and inheritance checks therefore
  cannot pass here, and no assertion grades them.
- The stub's fidelity is the measurement's ceiling. A response shape that differs from GitHub's can
  make either arm fail for a reason that has nothing to do with the skill. Read a failing run's
  `gh-calls.jsonl` before reading the failure as a skill effect.
- Every grader was replayed against one scripted good run and one scripted naive run before any
  model ran. The good runs passed every assertion, and the naive runs failed every assertion
  that is not a guard, except `nothing-changed` and `two-factor-reported` on `gog-01` and
  `selected-actions-only` on `gog-04`, which a naive run also passes.
- `gog-03`'s prompt asks for the change outright. `bypass-not-added` measures the skill's rule that
  a bypass actor is proposed and confirmed, which a reader may weigh against the request.

## Current state

No stamp yet, so `scripts/check_evals.py` reports the skill as unmeasured. Run it with:

```sh
python3 evals/run_eval.py tasks    --skill github-organization-governance --model sonnet --runs 3 --parallel 5
python3 evals/run_eval.py triggers --skill github-organization-governance --model sonnet --runs 3 --parallel 5
python3 evals/run_eval.py report   --skill github-organization-governance
```
