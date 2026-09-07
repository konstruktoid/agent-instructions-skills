# Terraform Coding Instructions

## Objective

Produce Terraform configuration that passes `terraform fmt`, `terraform validate`, and `tflint`
cleanly, keeps state and secrets out of version control, pins the versions it depends on, and
stays reviewable through its plan output. These instructions apply whenever an agent authors or
modifies Terraform configuration, meaning `.tf` and `.tf.json` files in modules and root
configurations, in a repository that adopts them.

The target is HashiCorp Configuration Language for Terraform 1.x. Where a repository runs
OpenTofu instead, the same rules apply and only the command name changes; invoke whichever binary
the repository already uses.

Two skills build on this document and are worth applying alongside it:

- For the state, secret, execution-identity, supply-chain, and policy concerns that
  `terraform validate` and `tflint` do not check on their own, apply the `terraform-secure-iac`
  skill (`skills/terraform/terraform-secure-iac/SKILL.md`).
- For adding or updating test coverage, apply the `terraform-testing` skill
  (`skills/terraform/terraform-testing/SKILL.md`), which covers discovering the repository's
  existing test approach, deciding when a test is required, and running the suite in a bounded
  verify loop. Test files are configuration, so the tooling baseline below applies to them too.

## Tooling

### Required

- Run checks through the repository's own entry point where one exists, for example `make`,
  `pre-commit run --all-files`, `terragrunt`, or the step in `.github/workflows/*.yml`, rather
  than a bare invocation that may use different options.
- Run `terraform fmt -recursive -check -diff` and fix what it reports. Write formatting changes
  only to files the change already touches.
- Run `terraform validate` after `terraform init -backend=false`. The `-backend=false` flag lets
  validation run without backend credentials or access to remote state.
- Run `tflint` with the repository's `.tflint.hcl`, including the provider plugin where the
  repository already configures one. It is the baseline lint gate, in the position `shellcheck`
  holds for shell.
- Pin the Terraform version with a `required_version` constraint in the `terraform` block, and
  pin every provider with a `version` constraint in `required_providers`. Use `~>` for a floating
  patch range, or `=` where the repository pins exactly.
- Commit `.terraform.lock.hcl`. Run `terraform providers lock` for every platform that CI and
  developers run on, so the lock file records a checksum for each.
- Keep `.terraform/`, `*.tfstate`, `*.tfstate.*`, `*.tfplan`, `crash.log`, `crash.*.log`,
  `.terraformrc`, `terraform.rc`, and any `*.tfvars` or `*.auto.tfvars` holding real values out
  of the repository through `.gitignore`.
- Generate module documentation with `terraform-docs` where the repository already uses it, and
  regenerate it when inputs or outputs change.

### Avoid

- Adding a linter, scanner, formatter, or test framework without first checking whether the
  repository already has an equivalent configured.
- Weakening `.tflint.hcl`, a scanner baseline, or a policy to make a failing check pass. Fix the
  configuration instead, or add a narrowly scoped, justified suppression.
- Running `terraform apply` without a saved, reviewed plan. Produce the plan with
  `terraform plan -out`, read it, then apply that file.
- Committing `*.tfstate`, `.terraform/`, a provider binary, a `*.tfvars` file with real values,
  or a `*.tfplan` file. A plan file can contain secret values in cleartext.
- Setting `version` inside a `provider` block. It is deprecated; the constraint belongs in
  `required_providers`.
- Sourcing a module from a branch or an unpinned Git reference. Pin to a release tag or a commit
  SHA, and for a registry module add a `version` constraint.
- Using `terraform.workspace` to switch between environments where the repository separates
  environments by directory and backend key. Match the pattern already in the repository.
- Reaching for a `local-exec` or `remote-exec` provisioner where a resource, a data source, or a
  provider already does the work. A provisioner runs outside the plan and leaves no trace in
  state.
- Hardcoding an account identifier, a region, a CIDR block, or another environment-specific value
  in a resource. Take it as a variable, or read it from a data source.

## Structure and Style

- One configuration root directory per state file. Separate environments by directory, each with
  its own backend key, rather than by `terraform.workspace` alone.
- Give a root or module the conventional files: `main.tf` for resources, `variables.tf`,
  `outputs.tf`, `versions.tf` for the `terraform` block and `required_providers`, `providers.tf`
  for provider configuration, and `README.md`. Split `main.tf` into files named by resource group
  once it grows past a screen or two.
- Name resources, data sources, variables, and outputs in `lower_snake_case`. Do not repeat the
  resource type in the name: `web`, not `web_instance`. Use a singular noun for a single object
  and a plural for a collection.
- Give every input variable a `type` and a `description`. Add a `validation` block where the
  value has a constrained domain, with a `condition` and a clear `error_message`. Mark a variable
  that carries a secret `sensitive = true`.
- Give every output a `description`. Mark an output `sensitive = true` when it carries a secret or
  a value derived from one.
- Prefer `for_each` over `count` for a set of named objects, so removing one entry does not
  re-index and recreate the others. Reserve `count` for a resource that is present or absent.
- Configure providers in the root module and pass them to child modules explicitly with the
  `providers` argument. Do not let a child module configure its own provider.
- Pin every module `source`. For a registry source, add a `version` constraint. For a Git source,
  append `?ref=` with a tag or a commit SHA. Prefer an internal module registry for shared
  modules over a public source.
- Apply a consistent tag or label set to every resource that supports one. Use the provider's
  `default_tags` or equivalent where it offers one, so the set is declared once.
- Lift a repeated or deeply nested expression into a `locals` block with a name that says what it
  is.

## Beyond What the Tools Check

`terraform validate` checks syntax, references, and types within a module. `tflint` adds
provider-aware checks for deprecated syntax and invalid values. The following still require
judgment because no static check settles them:

- **Whether state will hold a secret.** Many resources and data sources write attribute values to
  state in cleartext. Marking a variable or output `sensitive` hides it from CLI output, not from
  the state file. Keep the secret in an external manager and read it at apply time, or use an
  ephemeral resource or a write-only argument where the provider supports one.
- **Whether the plan was read.** The output of `terraform plan` is the review artifact for a
  change. A resource shown as replaced, a `-/+` line, or a changed argument the diff does not
  explain is a finding, not a detail to pass over.
- **Blast radius of the state layout.** One root for a whole environment means one lock, one set
  of credentials, and one failure domain. Smaller roots wired together through published outputs
  or `terraform_remote_state` limit what a single bad apply can reach.
- **The identity `apply` runs as.** It should hold only the permissions the configuration needs.
  `terraform plan` can run with read-only credentials; reserve write credentials for `apply`.
  Prefer short-lived federated credentials over static long-lived keys.
- **Whether a third-party module is trustworthy.** A module runs with the caller's credentials and
  can declare any resource type. Read it before adopting it, pin it to a fixed reference, and
  consider mirroring it into an internal registry rather than sourcing it from a moving one.
- **Drift.** Real infrastructure changes outside Terraform. A scheduled `terraform plan` that
  reports a non-empty diff is drift to investigate, not noise to clear with an immediate `apply`.
- **Upgrades.** A provider or module version bump can change a resource default or force
  replacement. Read the changelog, and run `plan` against a non-production root first.
- **User and system information in committed files.** No rule flags a real account identifier,
  organization name, internal IP, hostname, or email address that reached a `.tfvars` file, an
  example, a fixture, or generated documentation. Use placeholders (RFC 5737 addresses such as
  `192.0.2.0/24`, and `example.com`), take real values as variables, and normalize captured plan
  or apply output before writing it anywhere that gets committed.
- **Suppression justification.** `tflint` reports a rule disabled without a name, but not whether
  the reason next to a scoped `tflint-ignore` is a real one.

## Quality Checklist

Before considering a Terraform change complete, verify that:

- `terraform fmt -check` passes on every file touched.
- `terraform validate` passes after `terraform init -backend=false`.
- `tflint` passes on every file touched, with no new suppressions.
- `required_version` is set, every provider in `required_providers` carries a version constraint,
  and `.terraform.lock.hcl` is committed and updated for every platform CI uses.
- Every module `source` names a registry version, a tag, or a commit SHA, never a branch or an
  unpinned reference.
- No `*.tfstate`, `.terraform/` directory, provider binary, plan file, or `*.tfvars` with real
  values is staged.
- Every variable has a `type` and a `description`; every secret input and every secret-derived
  output is marked `sensitive`.
- The plan was saved with `-out` and read, not merely run. Every replacement and every unexplained
  change is accounted for.
- The judgment items above were considered, since the tools cannot check them.
- Nothing being committed carries a real account identifier, organization name, internal IP,
  hostname, or email address, including in `.tfvars` files, examples, fixtures, and generated
  documentation.
- Test coverage was added or updated if the change adds a module input or output, changes resource
  behavior, or fixes a bug, following the `terraform-testing` skill. If no test was added, the
  reason was stated rather than left implicit.
- The checks above were run, not merely described, and their output was seen. A change is not
  complete because the configuration looks right.
