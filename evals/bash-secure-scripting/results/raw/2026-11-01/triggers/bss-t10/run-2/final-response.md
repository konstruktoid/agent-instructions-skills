I couldn't find a shell task that creates an account, so I haven't changed anything.

The only Ansible role in the workspace is `roles/nginx`, and it has no `shell` or `command` tasks:

- `roles/nginx/tasks/main.yml` has two tasks: it installs nginx with `ansible.builtin.package` and renders `site.conf` with `ansible.builtin.template`.
- `roles/nginx/handlers/main.yml` is empty (`[]`).
- `roles/nginx/defaults/main.yml` only sets `nginx_worker_processes`.

I also searched the whole repo for `shell`, `command`, `useradd` and `adduser`. The only matches were in `README.md`. The repo has no `playbooks/` directory and no other roles.

The task may be on another branch, in a different repo, or not committed yet. If you paste it or tell me where it is, I'll swap it for `ansible.builtin.user`, keeping the same name, uid, groups, shell, home directory and system-account settings. Or, if you just want a new account-creation task added to the nginx role (for example, a system user for nginx), I can write that. Tell me the username and settings you want.
