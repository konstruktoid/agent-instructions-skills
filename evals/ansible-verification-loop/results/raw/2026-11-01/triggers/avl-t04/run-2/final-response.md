I couldn't find a playbook with short module names, so I haven't changed anything. Nothing was linted or tested either.

**What's in the workspace:**
- The only Ansible content is the `nginx` role. Its tasks in `roles/nginx/tasks/main.yml:3` and `:8` already use full names (`ansible.builtin.package`, `ansible.builtin.template`).
- `roles/nginx/handlers/main.yml` is an empty list, and `roles/nginx/defaults/main.yml` contains no module calls.
- There's no playbook file at all. The other YAML files are GitHub Actions, GitLab CI, docker-compose and k8s configs, none of which are Ansible.
- You may have meant to attach or paste the playbook, but it didn't come through.

**About "the repo's checks":**
- There are no Ansible checks to run. There's no `.ansible-lint`, `tox.ini`, `molecule/` directory or Makefile.
- `.gitlab-ci.yml` only runs `npm ci` and `npm run build`.

**What I can't do in this session:** I can read and search files, but I can't edit them or run commands. So even with the right playbook I couldn't apply the change or run `ansible-lint` here.

**Next steps:**
1. Send me the playbook's path, or paste its contents.
2. Run this in a session where I can edit files and run commands. I'll convert each short name to its full name (for example `copy` → `ansible.builtin.copy`, `service` → `ansible.builtin.service`) and run `ansible-lint` before and after to compare. Since the repo has no Ansible test setup, lint plus `ansible-playbook --syntax-check` is the most I can check.
