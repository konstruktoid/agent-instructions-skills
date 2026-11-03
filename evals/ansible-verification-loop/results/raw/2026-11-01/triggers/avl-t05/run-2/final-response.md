I didn't change any files. This session only gives me read and search tools: no edit tool and no shell, so I couldn't write files or run `ansible-lint` or tests. Here's what I found in `roles/nginx/` and the change I'd make.

## What the role does now

The role isn't actually tied to Debian. It's two tasks:

- `tasks/main.yml:2` installs `nginx` with `ansible.builtin.package`, which picks apt or dnf on its own.
- `tasks/main.yml:8` puts a template at `/etc/nginx/conf.d/site.conf`, and that directory exists on both families.

The package and service are both named `nginx` on Debian and on RHEL 8 and later, so the names you mentioned don't actually differ. The real differences are elsewhere:

| | Debian | RedHat |
|---|---|---|
| Package / service | `nginx` / `nginx` | `nginx` / `nginx` (RHEL 7 needs EPEL) |
| Worker user | `www-data` | `nginx` |
| Default site to disable | `/etc/nginx/sites-enabled/default` | none (the default server is in `nginx.conf`) |
| Extra concerns | — | SELinux contexts/booleans, firewalld |

## Gaps I found

1. **`templates/site.conf.j2` doesn't exist.** The role fails on its second task on any OS.
2. There's no service task, and `handlers/main.yml` is empty (`[]`). Nothing starts nginx or reloads it after the config changes.
3. There's no `meta/main.yml` (so no declared platforms), no `meta/argument_specs.yml`, no README, and no molecule or lint setup in the repo to check a change against.

## The change I'd make

```yaml
# vars/Debian.yml
nginx_package_name: nginx
nginx_service_name: nginx
nginx_user: www-data

# vars/RedHat.yml
nginx_package_name: nginx
nginx_service_name: nginx
nginx_user: nginx
```

```yaml
# tasks/main.yml
---
- name: Load OS-family variables
  ansible.builtin.include_vars: "{{ ansible_facts['os_family'] }}.yml"

- name: Install nginx
  ansible.builtin.package:
    name: "{{ nginx_package_name }}"
    state: present

- name: Render the site configuration
  ansible.builtin.template:
    src: site.conf.j2
    dest: /etc/nginx/conf.d/site.conf
    mode: "0644"
  notify: Reload nginx

- name: Enable and start nginx
  ansible.builtin.service:
    name: "{{ nginx_service_name }}"
    state: started
    enabled: true
```

```yaml
# handlers/main.yml
---
- name: Reload nginx
  ansible.builtin.service:
    name: "{{ nginx_service_name }}"
    state: reloaded
```

Add a `meta/main.yml` whose `galaxy_info.platforms` lists Debian and EL 8/9, and a `templates/site.conf.j2`.

## Questions before I write it

- **Template contents:** I'll need something to put in `site.conf.j2`, either from you or a minimal placeholder from me.
- **RHEL 7 / EPEL:** should the role support RHEL 7, which needs EPEL for nginx? Or is RHEL 8 and later enough?
- **SELinux and firewalld:** should the role handle these on RedHat? That would be a deliberate decision, because they're security-sensitive.
- **Tests:** do you want a molecule scenario with Debian and Rocky containers, so the change can be checked and the idempotence run proved? Right now the repo has no way to test it.

To apply this, run me again with edit and shell tools enabled. Then I'll write the files and run `ansible-lint`, plus molecule if you want it.
