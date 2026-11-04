# terraform-testing evals

This suite holds trigger probes only. It measures whether the skill's `description` routes a prompt
to it, and nothing about what the skill does once it fires. No task suite exists yet, so
`scripts/check_evals.py` reports the skill as unmeasured.

Five probes are in scope: a test for a new variable validation, a regression test for an output bug,
placing a test in an unfamiliar repository, covering a conditional resource, and extending an existing
Terratest suite. Five are out of scope. Two belong to `terraform-secure-iac` (a remote backend and an
unpinned module source), one is formatting, one is a Python test, and one is an explanation that needs
no code.

Run it with:

```sh
python3 evals/run_eval.py triggers --skill terraform-testing --model sonnet --parallel 5
python3 evals/run_eval.py report   --skill terraform-testing
```
