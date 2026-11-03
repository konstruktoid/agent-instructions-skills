I couldn't review `roles/postgres/tasks/main.yml` because it doesn't exist in this workspace. There's no `roles/postgres/` directory at all.

Here's what the repo has:

- **Ansible roles:** only `roles/nginx/`, with `tasks/main.yml`, `handlers/main.yml` and `defaults/main.yml`.
- **Mentions of Postgres:** only `docker-compose.yml`. That's a Compose service definition, not Ansible, so it has no Ansible package pinning or service restart handlers to check.
- **Other YAML:** `.github/workflows/deploy.yml`, `.gitlab-ci.yml` and `k8s/deployment.yml`.

Which of these did you mean?

1. **The Postgres role lives somewhere else:** another branch, an uncommitted path, or a different checkout. Point me to it and I'll review its package pinning and restart logic.
2. **You meant the nginx role:** I can review its package pinning and how its tasks notify handlers to restart the service.
3. **You meant the Postgres service in `docker-compose.yml`:** I can check its image tag pinning and `restart:` policy instead.
