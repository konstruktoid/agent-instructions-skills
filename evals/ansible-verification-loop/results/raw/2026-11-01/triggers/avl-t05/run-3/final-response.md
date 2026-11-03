I haven't changed anything. This session only gives me tools to read and search files, not to edit them or run commands, so I can't make the change or run `ansible-lint`/tests. Reading the role also showed that it isn't actually Debian-specific, which changes what "add RedHat support" means here.

## What `roles/nginx` contains

- `tasks/main.yml` installs `nginx` with `ansible.builtin.package` and renders `site.conf.j2` to `/etc/nginx/conf.d/site.conf`.
- `handlers/main.yml` is empty (`[]`).
- `defaults/main.yml` has only `nginx_worker_processes: auto`.
- There is no `meta/main.yml`, `vars/`, `templates/`, README, argument spec or Molecule scenario.

## The package and service names are already the same

- **Package:** it's called `nginx` on both Debian and RHEL 8/9 (AppStream; RHEL 7 needs EPEL). `ansible.builtin.package` picks apt or dnf by itself, so the install task already works on RedHat.
- **Service:** it's `nginx` on both. The role never manages the service anyway, so there's no service name to change.
- **Config path:** `/etc/nginx/conf.d/` exists and is loaded by default on both families.

## Real gaps, some of which affect Debian too

1. **The template is missing.** `templates/site.conf.j2` doesn't exist, so the template task fails on every OS.
2. **No service task and no handler.** Nginx is never started or enabled, and config changes never trigger a reload.
3. **RedHat-specific behaviour that does differ:**
   - The worker user is `nginx` on RHEL and `www-data` on Debian.
   - RHEL 7 needs EPEL.
   - With SELinux enforcing, a non-default port or docroot needs `http_port_t` or file context changes.
4. **No `meta/main.yml`,** so no supported platforms are declared.
5. **No tests,** so there's nothing to check RedHat support against.

## Proposed change

```yaml
# vars/Debian.yml
nginx_package: nginx
nginx_service: nginx
nginx_user: www-data

# vars/RedHat.yml
nginx_package: nginx
nginx_service: nginx
nginx_user: nginx

# tasks/main.yml (additions)
- name: Load OS-family variables
  ansible.builtin.include_vars: "{{ ansible_facts['os_family'] }}.yml"

- name: Install nginx
  ansible.builtin.package:
    name: "{{ nginx_package }}"
    state: present
# (render task gains: notify: Reload nginx)

- name: Enable and start nginx
  ansible.builtin.service:
    name: "{{ nginx_service }}"
    state: started
    enabled: true

# handlers/main.yml
- name: Reload nginx
  ansible.builtin.service:
    name: "{{ nginx_service }}"
    state: reloaded
```

It would also need a `meta/main.yml` listing Debian, EL 8 and EL 9, the missing `site.conf.j2`, and ideally a Molecule scenario on Debian plus Rocky/Alma 9 to check that converge and idempotence work on both families.

If you give me edit and shell access (or you'd rather apply this yourself), I can write these files and run `ansible-lint` and the tests. Do you also want EPEL handling for RHEL 7 and SELinux port/context handling, or only EL 8+ with the default ports?
