# probe-sandbox

A deliberately mixed repository used only by the trigger evals. It holds a small amount of
plausible material for every domain the probe prompts mention: an Ansible role, Terraform,
Kubernetes manifests, a GitHub Actions workflow, GitLab CI, a Jenkinsfile, a Dockerfile, a
Python package with tests, and a Go file.

Its purpose is to stop a probe from stalling on an empty directory. Routing is decided from
the skill description and the prompt, and this repository exists so the prompt has something
plausible to refer to.
