I couldn't find any task that uses the shell module to create an account, so I haven't changed anything.

The only Ansible role here is `roles/nginx`:
- `tasks/main.yml` has two tasks: installing nginx with `ansible.builtin.package` and rendering the site config with `ansible.builtin.template`.
- `handlers/main.yml` is an empty list.
- `defaults/main.yml` only sets `nginx_worker_processes`.

A search of the whole workspace for `shell`, `command`, `useradd` and `adduser` found nothing in any Ansible file.

The task might be on another branch or in a role that isn't checked out here. If you point me to it or paste it, I'll swap it for `ansible.builtin.user`. That would also make it idempotent, which a shell `useradd` isn't. If you want me to add an account task to the nginx role from scratch, send me:
- the username
- whether it's a system account
- its shell, home directory and groups
