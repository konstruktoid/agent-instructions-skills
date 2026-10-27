# terraform-secure-iac evals

Four feature requests, each against a fixture whose next change lands on a property the skill
covers: state kept in a local file on one laptop (`tsi-01`), a database password staged as a
literal variable default (`tsi-02`), an open-ended provider constraint and a Git module with no
`ref` (`tsi-03`), and a CI handover whose README runs `plan` on pull requests and `apply` on merges
(`tsi-04`).

No prompt mentions security, secrets, pinning, or least privilege. Every one is an ordinary
feature request, so only the skill can surface the rest.

Run it with:

```sh
python3 evals/run_eval.py tasks    --skill terraform-secure-iac --model sonnet --parallel 4
python3 evals/run_eval.py triggers --skill terraform-secure-iac --model sonnet --parallel 5
python3 evals/run_eval.py report   --skill terraform-secure-iac
```

## What the numbers can and cannot show

- `terraform` must be on the PATH of whoever runs the eval. Without it `fmt-clean` fails in both
  arms and measures nothing. The fixtures are already `fmt`-clean, so `fmt-clean` is a guard
  against an edit that breaks formatting; `fmt-actually-run` is the assertion that separates arms.
- `checkov` must be on the PATH or in `EVAL_TOOL_BIN`. `tsi-04`'s `iam-checks-clean` runs it with
  `--check` limited to the IAM ids. The fixtures' existing buckets, queue, and table fail several
  other checkov checks that no task asks about, and a full scan would charge them to both arms.
- No grader runs `terraform init`, so grading needs no registry access. In the harness sandbox
  `init` downloads the provider but `validate` fails to instantiate it, so no run can validate
  cleanly; `validate-result-reported` measures whether the agent said so rather than claiming a
  clean run. On 2026-10-26 every with-skill `tsi-01` run retried `validate` across both roots
  until it was truncated.
- `tsi-01`'s fixture holds an IAM access key, so its state carries a secret.
  `state-key-customer-managed` and `secret-in-state-reported` are the assertions that separate the
  arms there; the baseline already adds a bucket policy, so `state-bucket-access-restricted` is a
  guard.
- `tsi-03`'s labels module lives on `git.example.com`, which the agent cannot reach, so it cannot
  learn a real commit SHA or tag. Reporting the unpinned `ref` counts as the pass.
- `password-input-sensitive` passes vacuously when `db_password` is removed, as it is when the
  agent switches to `manage_master_user_password`. `password-kept-out-of-state` is the assertion
  that separates the arms on `tsi-02`; `sensitive` alone does not keep the value out of state.
- `tsi-01`'s state-bucket assertions search every `.tf` file, so versioning or encryption added to
  the existing reports bucket would also satisfy them.

Read the delta column first. A delta of zero means the baseline already handled that task and the
fixture needs a harder defect, not that the skill succeeded.

## Baseline state of the fixtures

Every fixture starts by failing nearly every assertion, which is the headroom the measurement
needs. The guards that pass on the unchanged fixture are the ones that assert an absence: no state
or plan file left behind, no credentials in a backend block, and on `tsi-04` no wildcard action,
no static keys, and no account identifier. A reference solution written against each fixture
passes every assertion that does not need `terraform`, so the set is achievable rather than
aspirational.
