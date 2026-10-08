I couldn't find a shell task that creates an account, so I haven't changed anything.

The only Ansible role in this workspace is `roles/nginx`:
- `tasks/main.yml` has two tasks: installing the nginx package and rendering a template. Neither runs a shell command.
- `handlers/main.yml` is empty (`[]`).
- `defaults/main.yml` sets only `nginx_worker_processes`.

A search of every `.yml`/`.yaml` file for `shell`, `command` or `useradd` found nothing. `scripts/backup.sh` is a standalone script, not part of the role.

The task may be on another branch or in a different repo. Could you point me to the file, or paste the task? If you'd rather I add the account to `roles/nginx` with the user module, tell me the username and any options (system account, shell, home directory, groups). The task would look like this:

```yaml
- name: Create the service account
  ansible.builtin.user:
    name: "{{ nginx_service_user }}"
    system: true
    shell: /usr/sbin/nologin
    create_home: false
    state: present
```

I'd also add `nginx_service_user` to `defaults/main.yml`.
