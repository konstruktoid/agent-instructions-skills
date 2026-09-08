# Terraform execution identity

Terraform acts on infrastructure as an authenticated identity: a cloud role, a service account, an
API token. That identity's permissions are the ceiling on what a mistake in configuration, a
compromised module, or a leaked credential can do.

## Least privilege

- Grant the identity that runs `terraform apply` only the permissions the configuration under
  management needs. Start from nothing and add permissions as a plan fails for lack of them,
  rather than starting broad and trimming later.
- Scope the identity per environment and, where practical, per configuration root. A production
  apply identity should not be able to touch development, or the reverse.
- Write policies with named actions and specific resource identifiers, not wildcards. A wildcard
  action or resource on the apply identity defeats the point of scoping it.
- Review the identity's granted permissions against what it has actually used, on a schedule, and
  remove what is unused.

## Separate plan and apply

- `terraform plan` needs only read access to refresh state and compute a diff. Run it with a
  read-only identity.
- Reserve write and delete permissions for `terraform apply`, behind a review or approval step.
- In a pull-request workflow, this means the plan that runs on the pull request uses read-only
  credentials and the apply that runs on merge uses the elevated ones.

## Short-lived credentials

- Prefer credentials issued per run that then expire: an OIDC exchange from the CI system to the
  cloud provider, an assumed role with a session limit, or a workload identity binding.
- Avoid static long-lived keys. Where they cannot be avoided, hold them in the CI secret store,
  never in the repository or a developer profile, and rotate them on a schedule.
- Do not write credentials to a file on disk or into a `provider` block. Let the provider's
  default credential chain pick them up from the environment.

## CI pipeline identity

- The workflow that runs Terraform is part of the trust boundary. Pin its actions by commit SHA,
  give its token the least privilege it needs, and do not expose cloud credentials to a workflow
  triggered by an untrusted fork.
- Run `apply` only from a protected branch or a protected environment, not from an arbitrary
  branch push or pull request.
