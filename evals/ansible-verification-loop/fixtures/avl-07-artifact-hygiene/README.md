# platform.storage

Storage roles for Debian and RedHat hosts.

Source: <https://github.com/platform/storage>

## Roles

| Role | Purpose |
|------|---------|
| `storage_lvm` | Applies a base LVM configuration. |

## Local setup

The molecule scenario needs the dependencies in `requirements.yml`, which `ansible.cfg`
installs into `./collections`, and reads its credentials from `.env.yml`. Both stay on the
machine they were created on.

```sh
ansible-galaxy collection install -r requirements.yml -p ./collections
make test
```

`make test` runs `ansible-lint` and then the molecule scenario, which writes its output to
`molecule-logs/`.

## Publishing

```sh
ansible-galaxy collection build
ansible-galaxy collection publish platform-storage-1.4.0.tar.gz
```
