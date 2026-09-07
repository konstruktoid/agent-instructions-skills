# Policy as code for Terraform

Static analysis of configuration and a review of the plan catch different classes of problem.
Policy as code turns an organization's rules into an automated gate rather than a checklist a
reviewer holds in mind.

## Where policy runs

- Against configuration, before a plan: a scanner such as `tfsec`, `trivy config`, `checkov`, or
  `terrascan` reads the `.tf` files and flags known misconfigurations.
- Against the plan, before apply: a framework such as Sentinel, Open Policy Agent with Conftest,
  or a provider-specific validator evaluates the planned actions and their attributes.
- The plan-based check is the stronger of the two, because it sees resolved values and computed
  attributes that a file-only scan cannot.

## Running policy

- Run the same policy set locally that the pipeline runs, so a violation is found before the pull
  request, not in CI.
- Gate the pipeline on severity: fail the run on high-severity findings so a change that trips one
  cannot merge. Lower severities can warn.
- Keep the policy set and any baseline or ignore file under review in the repository. An ignore
  entry needs a reason and, where the tool supports it, an expiry.
- Do not weaken a policy or extend a baseline to make an unrelated change pass. That is a
  separate, reviewed change with its own justification.

## What a policy set should carry

- Encryption at rest required on storage, databases, and disks.
- No storage bucket or object exposed to anonymous or public access.
- No security group or firewall rule open to the whole internet on an administrative port.
- IAM policies free of wildcard actions and wildcard resources.
- A required tag or label set on every resource that supports one.
- Deletion protection on stateful production resources, and a guard against destroying them.
- An approved list of regions, instance types, or images where the organization constrains them.
