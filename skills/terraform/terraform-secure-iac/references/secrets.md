# Secrets in Terraform

A secret in Terraform is exposed in three places: the configuration file, the state file, and the
plan and apply logs. A control that covers one does not cover the others.

## Keep secrets out of configuration

- Never write a password, API key, token, certificate, or private key as a literal in a `.tf`
  file or a committed `.tfvars` file.
- Take a secret as an input variable marked `sensitive = true`, and supply it from an external
  source: a secret manager data source, a `TF_VAR_` environment variable set by the CI secret
  store, or a `-var-file` that is not committed.
- Run secret scanning on the repository so a literal that slips in is caught before it reaches
  history. A secret that was ever committed is compromised until it is rotated.

## Keep secrets out of state

- Assume every attribute a resource or data source returns is stored in state in cleartext. See
  [state.md](state.md).
- Where the provider offers an ephemeral resource, a write-only argument, or an ephemeral input
  variable, use it so the value is never persisted to state or to a plan file. These need recent
  versions: ephemeral resources and variables from Terraform 1.10, provider write-only arguments
  from Terraform 1.11, and OpenTofu only from its own equivalent releases. On an older target,
  fall back to keeping the secret in an external manager and protecting the state and plan files
  as secret material.
- Where a secret must be generated, prefer a dedicated secret manager resource that keeps the
  value in the manager over a provider resource that returns it into state.
- A data source that reads a secret from a manager still places the retrieved value in state.
  Reading at apply time shortens the window the value is valid, but does not keep it out of state.

## Keep secrets out of logs

- Mark every output that carries a secret or a secret-derived value `sensitive = true`, so it is
  redacted from plan and apply output.
- `sensitive` redaction is not total: a value interpolated into a non-sensitive string, an error
  message from a provider, or a `-json` plan can still surface it. Do not rely on redaction as the
  only control.
- Ensure the CI system masks the secret in its job logs as well, independently of Terraform.
- Before pasting plan or apply output into an issue or a pull request, redact secret values and
  machine identifiers. Better, mark the source `sensitive` so there is nothing to redact.

## Sensitive markings

- `sensitive = true` on a variable propagates: an expression that uses it becomes sensitive, and
  Terraform errors if a sensitive value reaches an output or another position it would print
  without the marking carried through.
- Propagation and redaction are Terraform-CLI-scoped. They do not reach a provider's own debug
  logs, a `-json` plan consumed by other tooling, or the logs of an external secret manager the
  configuration calls. Those channels need their own controls.
- Do not remove a `sensitive` marking to quiet the propagation error. Find where the value is
  being exposed and stop the exposure.
