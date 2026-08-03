# probe-sandbox

A deliberately mixed repository used only by the trigger evals. It holds a small amount of
plausible material for every domain the probe prompts mention: an Ansible role, Terraform,
Kubernetes manifests, a GitHub Actions workflow, GitLab CI, a Jenkinsfile, a Dockerfile, a
Python package with tests, a Go file, and a shell script.

`scripts/backup.sh` was added on 2026-08-03, when the bash skills gained probes that refer to
a shell script. Trigger results measured before that date were measured without it.

Its purpose is to stop a probe from stalling on an empty directory. Routing is decided from
the skill description and the prompt, and this repository exists so the prompt has something
plausible to refer to.
