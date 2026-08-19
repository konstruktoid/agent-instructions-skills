# ansible-verification-loop evals

Six tasks over small Ansible roles and one collection. Three fixtures start `ansible-lint`
clean, so any finding at the end was introduced by the run; three start with existing findings
on the files the request forces the agent to touch, which is what exposes an agent that edits
without ever running the linter. The collection fixture's documented test entry point cannot
complete in this environment because molecule is not installed, which is deliberate: the
skill requires naming the failing check and including its output rather than declaring
success unverified, and `lint-clean-or-reported` encodes exactly that disjunction by reading
the run's final message. Run it with `python3 evals/run_eval.py tasks --skill
ansible-verification-loop`, then `report`. `lint-clean` and `lint-clean-or-reported` are
graded separately so an honest stop is distinguishable from a clean pass.

`avl-05-collection-review` carries `"timeout_seconds": 3600` in `tasks.json`, double the
default. Its fixture README documents `make test` as the entry point, and that target runs
`ansible-lint` and then the molecule scenario, which boots a systemd container and installs
packages inside it. The 2026-07-25 run reached 1474 s and was still waiting on that scenario
when the process returned, which is how it ended up graded on a mid-loop status line. The
raised ceiling gives the scenario room to finish inside the run instead.

`avl-06-autofix-cosmetics` is the only task graded on something no linter reports. Every finding
in its fixture is repairable by `ansible-lint --fix`, and that same run deletes the blank line
after each flow-style value in `defaults/main.yml`, joining the following comment block to the
value above it. No rule fires before or after, so the run passes either way and the damage is
visible only in `git diff`. `autofix-cosmetics-preserved` asserts that no comment block follows a
non-blank, non-comment line, which fails on the auto-fixer's output and passes on the fixture as
shipped. `lint-clean` still has to pass alongside it, so reverting the whole `--fix` run and
leaving the findings in place does not score.

That task depends on a behavior of `ansible-lint --fix` rather than on a documented rule, and
`evals/README.md` installs the tool unpinned. Confirm the deletion still happens before reading a
pass as evidence: run `ansible-lint --fix .` in a copy of the fixture and check that `git diff`
removes the blank lines. A release that stops deleting them leaves the assertion passing without
separating a reviewed diff from a trusted summary, and the fixture then needs a new defect.

That task has never been graded. `results/2026-07-28-isolation.md` covers `avl-03` alone, and
`results/2026-07-25.md` predates the task, so the suite's measured coverage is five of its six
tasks.
