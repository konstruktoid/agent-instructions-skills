I couldn't find a shell task that creates an account, so I haven't changed anything.

The only role in the repo is `roles/nginx`. Its `tasks/main.yml` has two tasks: one installs the package and one renders a template. Nothing under `roles/` mentions `shell`, `command`, `user`, `useradd` or `adduser`. A repo-wide search for `shell:` also found nothing.

The role may be on another branch, in a different repository, or not committed yet. If you can tell me where it lives, I'll make the change there.

If you'd like the task written from scratch, I'd need the account details:

- the username
- the groups it should belong to
- its login shell
- whether it's a system account
- its home directory

The task would look like this:

```yaml
- name: Create the service account
  ansible.builtin.user:
    name: <username>
    system: true
    shell: /usr/sbin/nologin
    create_home: false
    state: present
```

The `user` module is idempotent, so it replaces any `id ... || useradd ...` guard the old shell task had.
