I didn't change anything, because there's no shell task that creates an account in this repository.

The only Ansible role is `roles/nginx`:

- **`tasks/main.yml`** has two tasks. One installs nginx with `ansible.builtin.package`, and the other writes the site config with `ansible.builtin.template`. Neither uses `shell` or `command`.
- **`handlers/main.yml`** is empty (`[]`).
- **`defaults/main.yml`** only sets `nginx_worker_processes`.

I also searched the whole repository for `useradd`, `adduser`, `shell:`, `ansible.builtin.shell` and `command:`, and none of them appear.

The task you mean may be on another branch, in a role that hasn't been committed or copied here, or in a separate roles repository. If you point me to it or paste it in, I'll rewrite it with `ansible.builtin.user`. That includes choosing whether it's a system account, its shell (for example `/usr/sbin/nologin` for a service account), its home directory and its groups, so it stays idempotent and doesn't run shell commands.
