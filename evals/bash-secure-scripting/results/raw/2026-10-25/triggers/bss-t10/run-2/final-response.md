I didn't change anything, because the repo has no shell task that creates an account.

The only Ansible role is `roles/nginx`:
- `tasks/main.yml` has just two tasks: install nginx with `ansible.builtin.package` and render the site config with `ansible.builtin.template`.
- `handlers/main.yml` is empty (`[]`).
- `defaults/main.yml` only sets `nginx_worker_processes`.

I also searched every file in the workspace for `shell:`, `ansible.builtin.shell`, `ansible.builtin.command`, `useradd` and `adduser`, and found no matches.

The task may be on another branch, in a role that isn't committed yet, or in a separate roles repo. If you paste it or tell me where it is, I'll swap it out. The replacement will usually look like this:

```yaml
- name: Create the service account
  ansible.builtin.user:
    name: "{{ app_user }}"
    system: true
    shell: /usr/sbin/nologin
    create_home: false
    state: present
```

I'll match the options to whatever flags your `useradd` call passes, such as `-u`, `-g`, `-G`, `-d` or `-m`. Unlike the shell version, this task is idempotent: it won't fail or report a change when the account already exists.
