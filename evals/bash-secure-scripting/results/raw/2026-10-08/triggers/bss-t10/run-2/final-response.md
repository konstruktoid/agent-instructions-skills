I couldn't find a `shell` task that creates an account, so I haven't changed anything.

The only Ansible role in this repo is `roles/nginx`:

- `roles/nginx/tasks/main.yml` has two tasks. One installs nginx with `ansible.builtin.package` and the other renders `site.conf.j2` with `ansible.builtin.template`. Neither uses `shell` or `command`.
- `roles/nginx/handlers/main.yml` is empty (`[]`).
- `roles/nginx/defaults/main.yml` only sets `nginx_worker_processes`.

I also searched every YAML file in the workspace for `shell`, `command` and `useradd`, and nothing matched.

The task you mean may be in another branch, another repo, or a file that isn't committed here. You can point me to it or paste it in. Or, if you want a new account task in the nginx role, it would look like this:

```yaml
- name: Create the service account
  ansible.builtin.user:
    name: "{{ nginx_service_user }}"
    system: true
    shell: /usr/sbin/nologin
    create_home: false
    state: present
```

`nginx_service_user` would be a new variable in `defaults/main.yml`. Before I add it, I need the account's name, UID/group, home directory and login shell, so it matches what your current `shell` command creates.
