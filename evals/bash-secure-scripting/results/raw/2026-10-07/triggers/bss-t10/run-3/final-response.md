I couldn't find a shell task that creates an account, so I haven't changed anything.

- **Only role:** `roles/nginx` is the only Ansible role in the repo. Its `tasks/main.yml` has two tasks, `package` to install nginx and `template` to render `site.conf`. Neither uses `shell`.
- **Searches:** I searched the whole workspace for `shell:`, `command:`, `useradd`, `adduser`, `usermod`, `chpasswd` and "user". The only "account" hits are the ledger code in `src/ledger/balance.py` and its test, which have nothing to do with Ansible.
- **Handlers and defaults:** I only searched those files and didn't open them.

The role may be on another branch, in another repo, or not committed yet. If you can tell me where it lives, I'll make the change.

If you want me to add the account to the nginx role instead, I need a few details:
- The username.
- The group, if any.
- The shell.
- Whether it's a system account.
- The home directory.

It would look like this:

```yaml
- name: Create the service account
  ansible.builtin.user:
    name: <name>
    system: true
    shell: /usr/sbin/nologin
    state: present
```
