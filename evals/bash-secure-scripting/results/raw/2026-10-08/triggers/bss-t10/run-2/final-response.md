I couldn't find a shell task that creates an account, so I haven't changed anything.

This workspace has one Ansible role, `roles/nginx`, and none of its files uses `shell`, `command` or `useradd`:

- `roles/nginx/tasks/main.yml` has two tasks: install nginx with `ansible.builtin.package` and write the site config with `ansible.builtin.template`.
- `roles/nginx/handlers/main.yml` is empty (`[]`).
- `roles/nginx/defaults/main.yml` sets only `nginx_worker_processes: auto`.

A search of every `.yml` and `.yaml` file for `shell`, `command` and `useradd` also found nothing. The task may be in another branch, another repo, or a file that isn't checked in here.

If you paste the task or tell me where it is, I'll swap it out. Here is roughly what the replacement would look like:

```yaml
- name: Create the service account
  ansible.builtin.user:
    name: "{{ nginx_service_user }}"
    system: true
    shell: /usr/sbin/nologin
    create_home: false
    state: present
```

I'd match the options to what the original `useradd` call does (UID, group, home directory and so on). The user module only changes the account when it doesn't already match, so this also fixes the usual problem with shell tasks: they report "changed" or fail on every run after the first.
