I couldn't review it because `roles/postgres/tasks/main.yml` isn't in this workspace. There's no `roles/postgres/` directory at all, and nothing named `postgres` anywhere in the tree.

The only Ansible role here is `roles/nginx`, which has `tasks/main.yml`, `handlers/main.yml` and `defaults/main.yml`. The workspace also has `.github/workflows/deploy.yml`, `.gitlab-ci.yml`, `docker-compose.yml` and `k8s/deployment.yml`.

I don't want to guess what the postgres role contains, so tell me which of these you want:

1. **A different path or branch.** If the postgres role is somewhere else or on another branch, give me the path and I'll review the pinning and restart logic.
2. **Paste the file.** I can review the task file and its `defaults/` and `handlers/` from the text.
3. **The nginx role instead.** If that's the one you meant, I can check its package pinning and handler-based restart logic.

Whichever you choose, I can only review it by reading the files. I don't have a shell in this session, so I can't run `ansible-lint` or molecule to check anything.
