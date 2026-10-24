I didn't change anything, because I couldn't find a task that creates an account with the shell module. This repo has one Ansible role, `roles/nginx`, and none of its files run a shell command:

- `roles/nginx/tasks/main.yml` has two tasks: install nginx with `ansible.builtin.package` and render `site.conf` with `ansible.builtin.template`.
- `roles/nginx/handlers/main.yml` is empty (`[]`).
- `roles/nginx/defaults/main.yml` only sets `nginx_worker_processes: auto`.

A search of all YAML files found no `shell:`, `command:` or `useradd` lines.

The task may be on another branch, in a role not committed yet, or in a different repo. If you paste it or tell me where it is, I'll replace it. The replacement would look like this:

```yaml
- name: Create the service account
  ansible.builtin.user:
    name: "{{ app_user }}"
    group: "{{ app_group }}"
    shell: /usr/sbin/nologin
    system: true
    create_home: false
    state: present
```

Unlike a raw `useradd` call, the user module is idempotent: it doesn't fail when the account already exists, and check mode works. It also takes the username as a parameter, so it never goes through a shell. I'd match the account's settings (UID, groups, home, shell) to whatever your current task does.
