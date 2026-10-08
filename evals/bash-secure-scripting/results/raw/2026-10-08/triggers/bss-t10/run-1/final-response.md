I didn't change anything, because this workspace has no shell task that creates an account.

The only Ansible role here is `roles/nginx`, and none of its files contain one:

- `roles/nginx/tasks/main.yml` has two tasks: `ansible.builtin.package`, which installs nginx, and `ansible.builtin.template`, which renders `site.conf`.
- `roles/nginx/handlers/main.yml` is empty (`[]`).
- `roles/nginx/defaults/main.yml` only sets `nginx_worker_processes`.

I also searched every YAML file in the workspace for `shell`, `command` and `useradd`, and nothing matched.

The task may be in another role, another branch, or a file that hasn't been added yet. If you tell me where it is or paste it, I'll swap it for `ansible.builtin.user`. That would look something like this:

```yaml
- name: Create the nginx service account
  ansible.builtin.user:
    name: "{{ nginx_user }}"
    system: true
    shell: /usr/sbin/nologin
    home: /var/lib/nginx
    create_home: false
    state: present
```

I'd copy the exact options (UID, groups, home directory, shell) from your current `useradd` flags so the account comes out the same.

Or, if you just want an account task added to the nginx role, I can add it to `tasks/main.yml` before the template task and add `nginx_user` to the defaults. Tell me the account name and options you want.
