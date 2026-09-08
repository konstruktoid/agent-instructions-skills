# Terraform state protection

The state file records every resource Terraform manages and their attributes, many in cleartext.
Read access to state is equivalent to read access to the credentials and data those attributes
describe. Write access to state is the ability to make Terraform create, change, or destroy real
infrastructure on the next run.

## Remote backend

- Store state in a remote backend, not on a developer machine and never in version control. Add
  `*.tfstate` and `*.tfstate.*` to `.gitignore`.
- Enable encryption at rest on the backend. Use a customer-managed key where the backend and the
  threat model call for one.
- Restrict backend access to the CI identity and a small set of administrators. A read of the
  bucket or container is a read of every secret in state.
- Enable object versioning on the backend so a corrupt or truncated state can be rolled back.
- Enable state locking so two runs cannot write concurrently. Where the backend needs a separate
  lock table or lease mechanism, configure it; a missing lock corrupts state under concurrency.
- Keep the backend configuration in a `backend` block or a `-backend-config` file that is under
  review, not passed ad hoc on the command line. Put only non-secret metadata there, meaning the
  bucket, key, region, and table names. Supply backend credentials through environment variables
  or the backend's default credential chain, never in a reviewed file.

## State as a secret store

- Assume any attribute a resource or data source returns is in state in cleartext, including
  generated passwords, private keys, and connection strings.
- Marking a variable or output `sensitive` removes it from CLI output only. It does not encrypt
  state and does not stop the value being read from the state file.
- Prefer reading a secret from an external manager at apply time over having Terraform generate or
  store it. Where the provider offers an ephemeral resource or a write-only argument, use it so
  the value never lands in state. See [secrets.md](secrets.md).
- A plan file (`terraform plan -out`) can also contain secret values. Treat it like state: do not
  commit it, and delete it after apply.

## Blast radius

- One state file for an entire environment means one lock, one credential set, and one failure
  domain. A single bad apply can reach everything in it.
- Split configuration into smaller roots along ownership and rate-of-change boundaries. Wire them
  together through published module outputs or a `terraform_remote_state` data source.
- A `terraform_remote_state` data source exposes only the other configuration's root module
  outputs to Terraform expressions, but reading them requires the caller to have read access to
  the complete state snapshot, which may hold every secret in it. Prefer narrow, explicit
  outputs, or a dedicated data store for shared values, over granting a reader access to a whole
  team's state.

## Migrations

- Run a state migration (`terraform state mv`, `import`, `-migrate-state`) as a reviewed change,
  not an unrecorded manual step. Prefer `import` and `moved` blocks in configuration over CLI
  commands, so the change is in version control.
- Back up the state file before a migration. The backend's versioning is that backup; confirm it
  is on first.
