I didn't change anything, because this repo has no shell task that creates an account.

The only Ansible role is `roles/nginx`:
- `roles/nginx/tasks/main.yml` has two tasks: installing nginx with `ansible.builtin.package` and rendering the site config with `ansible.builtin.template`.
- `roles/nginx/handlers/main.yml` is empty (`[]`).
- `roles/nginx/defaults/main.yml` only sets `nginx_worker_processes`.

I searched the whole workspace for `useradd`, `adduser`, `shell` and `command`. None of them show up in any YAML file. The task you mean may be on another branch, in another repo, or not committed yet.

If you can point me to it or paste it, I'll swap it out. The usual replacement looks like this:

```yaml
- name: Create the service account
  ansible.builtin.user:
    name: "{{ app_user }}"
    system: true
    shell: /usr/sbin/nologin
    create_home: false
    state: present
```

I'll copy the details from your existing `useradd` flags, such as UID, groups, home directory and comment. If you'd rather I add an account task to the nginx role from scratch, tell me the username and whether it should be a system account.
