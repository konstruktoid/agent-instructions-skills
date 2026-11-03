I don't have a file-writing tool in this session, so here is the script for you to save as `print_groups.py` next to `inventory.ini`:

```python
#!/usr/bin/env python3
"""Print hosts from a static Ansible INI inventory, grouped by group name."""

import sys
from collections import OrderedDict


def parse_inventory(path):
    groups = OrderedDict()
    children = {}
    current = "ungrouped"
    section_type = "hosts"

    with open(path, encoding="utf-8") as fh:
        for raw in fh:
            line = raw.split("#", 1)[0].split(";", 1)[0].strip()
            if not line:
                continue

            if line.startswith("[") and line.endswith("]"):
                name = line[1:-1].strip()
                if ":" in name:
                    name, section_type = name.split(":", 1)
                else:
                    section_type = "hosts"
                current = name
                if section_type in ("hosts", "children"):
                    groups.setdefault(current, [])
                continue

            if section_type == "hosts":
                host = line.split()[0]  # drop inline vars like ansible_host=...
                if host not in groups.setdefault(current, []):
                    groups[current].append(host)
            elif section_type == "children":
                children.setdefault(current, []).append(line.split()[0])
            # [group:vars] sections are ignored

    return groups, children


def resolve(group, groups, children, seen=None):
    """Return the group's own hosts plus the hosts of its child groups."""
    seen = seen or set()
    if group in seen:
        return []
    seen.add(group)
    hosts = list(groups.get(group, []))
    for child in children.get(group, []):
        for h in resolve(child, groups, children, seen):
            if h not in hosts:
                hosts.append(h)
    return hosts


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "inventory.ini"
    groups, children = parse_inventory(path)

    for group in groups:
        hosts = resolve(group, groups, children)
        if group == "ungrouped" and not hosts:
            continue
        print(f"{group}:")
        for host in hosts:
            print(f"  {host}")


if __name__ == "__main__":
    main()
```

Run it with:

```
python3 print_groups.py inventory.ini
```

I haven't run it, but when I trace it by hand against your current `inventory.ini`, it should print:

```
web:
  web01.example.com
  web02.example.com
db:
  db01.example.com
```

Your inventory is just two plain groups. The script also handles a few things you might add later:
- **Variables on a host line** (`web01 ansible_host=10.0.0.1`): it keeps only the hostname.
- **`[group:children]`**: a parent group lists the hosts of its child groups.
- **`[group:vars]`**: these sections are skipped.
- **Comments** starting with `#` or `;`: ignored.
- **Hosts above the first header**: they go under `ungrouped`.

It does **not** expand host ranges like `web[01:10].example.com`. If you need that, or full Ansible behaviour, `ansible-inventory -i inventory.ini --graph` gives a similar tree using Ansible's own parser.
