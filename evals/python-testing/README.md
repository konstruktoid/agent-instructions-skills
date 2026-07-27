# python-testing evals

Five tasks, each against a fixture with a deliberately distinct existing test layout, because
the skill's first claim is that the layout is discovered and matched rather than replaced.
One fixture keeps its checks inside the package as `check_*` functions configured through
`pyproject.toml`, and a run that invents a conventional `tests/` directory beside it fails
`no-checks-added-to-the-stale-directory`. One task is a refactor with no behaviour change, where
the skill's own table says a test is not required and its absence must be stated; there,
adding a test is the wrong answer and `existing-tests-unchanged` is the pass condition. The
bug-fix task is graded by copying the finished workspace, restoring `src/` to the fixture
commit, and requiring the suite to fail, which is the only mechanical way to check that a
regression test fails against the unfixed code. Run it with `python3 evals/run_eval.py tasks
--skill python-testing`, then `report`.

## Fixtures hardened on 2026-07-27

`pt-02`, `pt-04`, and `pt-05` scored full marks in both arms on 2026-07-25, which measures task
difficulty rather than skill effect. Each now carries a pre-existing helper that is wrong in a
way its own docstring conceals:

- `pt-02`: `is_holiday` compares a `date` against a list of ISO strings, so it always returns
  False, and `days_between` counts both ends while reading as an ordinary day count. The task
  now asks for working days rather than weekdays, so both helpers are on the path.
- `pt-04`: `uploads.naming.base_name` strips a directory component instead of rejecting it and
  misses a backslash, `extension_of` returns the whole name when there is no dot, and
  `ALLOWED_EXTENSIONS` is case sensitive against a task that requires lowercasing.
- `pt-05`: `_tests/_helpers.check_values` prints a mismatch rather than raising, and one
  existing check already uses it, so following the house style produces coverage that cannot
  fail. A stale top-level `tests/` directory sits beside the collected `src/ledger/_tests/`,
  and `pyproject.toml` excludes it. `added-checks-fail-when-the-feature-breaks` copies the
  finished workspace, appends a `running_balance` that returns an empty list, and requires the
  suite to fail.

The results files under `results/` predate this change. Every number in `results/2026-07-25.md`
was measured against the previous fixtures and is not comparable to anything measured after
this date.
