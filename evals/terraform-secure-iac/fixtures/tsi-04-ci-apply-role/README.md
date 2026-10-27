# ingest

Terraform for the ingest pipeline: a landing bucket, an event queue, and a checkpoint table.

Today an engineer runs `terraform apply` from a laptop. The `platform/ingest` repository's GitHub
Actions workflow is meant to take that over, running `plan` on pull requests and `apply` on merges
to `main`.
