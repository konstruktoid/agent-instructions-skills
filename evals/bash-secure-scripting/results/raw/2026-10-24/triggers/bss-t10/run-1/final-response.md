I didn't change anything, because the repo has no shell task that creates an account.

The only Ansible role is `roles/nginx`:

- `roles/nginx/tasks/main.yml` has just two tasks: one installs nginx with `ansible.builtin.package` and one renders `site.conf.j2` with `ansible.builtin.template`.
- `roles/nginx/handlers/main.yml` and `roles/nginx/defaults/main.yml` don't run any commands either.

Searching every file for `shell`, `command`, `useradd` and `adduser` turned up nothing except two mentions of "shell script" in the README. `scripts/backup.sh` is a standalone Bash script, not part of the role.

The task you mean may be on another branch, or the change may not be committed or pushed yet. If you paste the task or tell me where it is, I'll swap it for `ansible.builtin.user`. Or, if you give me the account details (name, system account or not, shell, home directory, groups), I can add a new `ansible.builtin.user` task to the nginx role. It would look like this:

```yaml
- name: Create the service account
  ansible.builtin.user:
    name: "{{ nginx_service_user }}"
    system: true
    shell: /usr/sbin/nologin
    create_home: false
    state: present
```

I'd also add a default for `nginx_service_user` in `defaults/main.yml`.
