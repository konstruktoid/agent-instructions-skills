# Contributing

Open a pull request against `main`. CI runs the `lint` and `test` jobs in
`.github/workflows/ci.yml`.

Repository rulesets are kept as JSON under `.github/rulesets/`, one file per ruleset, and applied
with `gh api --input`.
