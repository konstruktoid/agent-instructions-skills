# python-testing evals

Five tasks, each against a fixture with a deliberately distinct existing test layout, because
the skill's first claim is that the layout is discovered and matched rather than replaced.
One fixture keeps its checks inside the package as `check_*` functions configured through
`pyproject.toml`, and a run that invents a conventional `tests/` directory beside it fails
`no-conventional-tests-dir-created`. One task is a refactor with no behaviour change, where
the skill's own table says a test is not required and its absence must be stated; there,
adding a test is the wrong answer and `existing-tests-unchanged` is the pass condition. The
bug-fix task is graded by copying the finished workspace, restoring `src/` to the fixture
commit, and requiring the suite to fail, which is the only mechanical way to check that a
regression test fails against the unfixed code. Run it with `python3 evals/run_eval.py tasks
--skill python-testing`, then `report`.
