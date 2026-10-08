I couldn't find a task that uses the shell module to create an account, so I haven't changed anything.

- The only role in the repo is `roles/nginx`. Its `tasks/main.yml` has two tasks: one installs the package and one renders a template.
- I searched the whole repo for `shell:`, `command:`, `ansible.builtin.shell` and `useradd`/`adduser`/`usermod`/`chpasswd`. Nothing matched.

The role you mean may be on another branch, in a different repo, or not committed yet. Can you give me its path or tell me which branch it's on?

It would also help to know:
- the account name
- the shell, home directory, groups, and whether it's a system account
- whether the existing task sets a password or an SSH key

Once I can see the task, I'll replace it with `ansible.builtin.user`.
