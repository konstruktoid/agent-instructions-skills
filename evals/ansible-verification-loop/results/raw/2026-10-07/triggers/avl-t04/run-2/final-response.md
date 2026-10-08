I didn't change anything, because the playbook already uses FQCN throughout. Nothing was left to convert.

- **`roles/nginx/tasks/main.yml`:** both tasks already use `ansible.builtin.package` and `ansible.builtin.template`.
- **Other YAML files:** a search for short module names (`package`, `template`, `copy`, `service`, `command`, `shell`, and similar) across the repo found none. The only hit was `template:` in `k8s/deployment.yml`, which is a Kubernetes pod spec, not an Ansible task.
- **Playbook:** I found no playbook file, only the `nginx` role. If you meant a playbook that isn't in this checkout, tell me where it is.
- **Repo checks:** the repo has no `tox.ini`, `Makefile`, `.ansible-lint` or molecule setup. The only CI file is `.github/workflows/deploy.yml`, which doesn't run `ansible-lint` or any Ansible test. I didn't run `ansible-lint` on an unchanged tree, so I can't say it passes. There was no edit to verify.

I noticed some things outside this task and left them alone.

- **`roles/nginx/handlers/main.yml`:** it contains `[]`, an empty handler list, so nothing reloads nginx after the template task changes the config.
- **`.github/workflows/deploy.yml`, permissions:** it sets `permissions: write-all` on a `pull_request` trigger.
- **`.github/workflows/deploy.yml`, title injection:** it interpolates `github.event.pull_request.title` directly into a `run:` step. A crafted PR title could inject shell commands into that step, which runs with write-all permissions.
