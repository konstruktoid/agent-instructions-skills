I didn't change anything, because the role in this workspace doesn't have a shell task that creates an account.

The only role is `roles/nginx`:

- **`tasks/main.yml`** has two tasks: it installs nginx with `ansible.builtin.package` and renders `site.conf.j2` with `ansible.builtin.template`. There's no `shell`, `command`, `useradd` or `adduser`.
- **`handlers/main.yml`** is empty (`[]`).
- **`defaults/main.yml`** only sets `nginx_worker_processes`.

I also searched every YAML file in the repo for `shell`, `command`, `useradd` and `adduser`, and found nothing.

The task may be on another branch, in a role that hasn't been committed here, or in a different repo. If you paste the task or tell me where it is, I'll convert it. Here's the shape the replacement usually takes, so you can check it fits:

```yaml
- name: Create the service account
  ansible.builtin.user:
    name: "{{ app_user }}"
    system: true
    shell: /usr/sbin/nologin
    home: /var/lib/app
    create_home: false
    state: present
```

I'll match the flags your current `useradd` call uses (UID, group, home directory, shell, comment), so the account comes out the same as it does now.
