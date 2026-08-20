# ansible-verification-loop evals

Seven tasks over small Ansible roles and two collections. Four fixtures start `ansible-lint`
clean, so any finding at the end was introduced by the run; three start with existing findings
on the files the request forces the agent to touch, which is what exposes an agent that edits
without ever running the linter. The documented test entry point of `avl-05-collection-review`
cannot complete in this environment because molecule is not installed, which is deliberate: the
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

`avl-07-artifact-hygiene` is the only task whose subject is what the verify loop leaves behind
rather than what it reports. Its fixture is a collection whose `galaxy.yml` lists `.ansible/`,
`.cache/`, `.github/` and `collections/` under `build_ignore`, each written with the trailing
slash that `ansible-galaxy collection build` never matches, and whose `.gitignore` covers only
`*.tar.gz`. Downloaded dependencies, a molecule log carrying a hostname, a username, a home
directory path and an internal address, a compat cache and an `.env.yml` of credentials all sit
in the working copy, so a build ships every one of them. Outside this harness a lint run adds
one more, installing the collection into `.ansible/` for the next build to package recursively,
which is the shape the 26M artifact in konstruktoid/ansible-collection-hardening#91 had. That
does not happen here: `run_eval.py` points `ANSIBLE_HOME` at each run's private home, so
`.ansible/` never appears in the workspace and no assertion may require it to be ignored. The
hostname, the username and the address in the log are invented, and the address is from RFC
5737.

The hygiene assertions all fail on the fixture as shipped and all pass once both lists are
corrected, which was confirmed by hand before the task was first run rather than inferred from
the assertion text. `local-state-preserved` closes the shortcut of deleting the files instead of
ignoring them, and the two artifact assertions build the collection and read the tarball, so a
`build_ignore` list that merely reads correctly does not score. They need `ansible-galaxy`, which
`uv tool install ansible-lint` does not expose; `evals/README.md` installs `ansible-core`
alongside it for that reason.

Two of avl-07's assertions were corrected after the 2026-08-20 runs, and that stamp reports the
regraded numbers rather than the ones the runs first produced. As first written, the four
`.gitignore` entries and `.ansible` were a single five-way conjunction, and it scored the
with-skill run, which covered four of the five, exactly as it scored the baseline, which covered
none: 10/12 against 10/12, a delta of zero. Splitting it per category and dropping the
unobservable `.ansible` term reports the same two runs as 15/16 against 10/16. `git rm --cached`
on the already-tracked local state was deliberately left ungraded before those runs, as a
judgment call either way; the with-skill run did it and explained why, the baseline did neither,
and step 8 puts a file that is still in the index inside the repository, so
`local-state-untracked` grades it now. Both corrections were made with that pair of runs in view
and both favour the skill, which on its own is weaker evidence than a check written before the
fact.

`results/2026-08-20-repeat.md` is what answers that. It repeats the same task three times per
condition against the corrected assertions, which were in place before any of those six runs, so
it measures checks fixed in advance rather than after it. The with-skill condition scored 15/16
in all three runs and the baseline 9, 9 and 10, ranges that do not overlap, at 1.2x the cost.
The two conditions diverge on the same points every time: no baseline run touched `.gitignore`
at all or untracked anything, and two of the three never ran `ansible-lint`, while all three
with-skill runs fixed both lists, untracked the local state without deleting it, and built the
artifact to check what it held.

`build-ignore-covers-gitignore` is the one assertion that failed in all eight runs across both
stamps and both conditions, always on the same entry: `*.tar.gz` was already in `.gitignore` and
no run gave it a `build_ignore` counterpart. No transcript argues the point, so this reads as an
entry nobody carried across rather than a considered omission. The build ignores only
`<namespace>-<name>-*.tar.gz` in the root on its own, so any other tarball there still ships, and
the checklist item the assertion comes from is explicit. Changing the skill to make that more
prominent would invalidate this stamp and would be tuning the skill to its own eval, so it is
recorded here instead.

`results/2026-08-20-repeat.md` and `results/2026-08-20.md` both cover `avl-07` alone,
`results/2026-07-28-isolation.md` covers `avl-03` alone, and `results/2026-07-25.md` predates
both, so the suite's measured coverage is six of its seven tasks. Both 2026-08-20 stamps were
measured against an uncommitted working tree, so `check_evals.py` reports the newer one as
unreproducible until the task is run again from a clean checkout.
