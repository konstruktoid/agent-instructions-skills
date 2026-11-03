I can't create files in this session because I don't have a write or shell tool, so here's the script to save as `print_inventory_groups.py`. I also couldn't run it, so it hasn't been tested.

It reads `inventory.ini`, which currently has two groups: `web` (web01, web02) and `db` (db01).

```python
#!/usr/bin/env python3
"""Print hosts from a static Ansible INI inventory, grouped by group name."""

import argparse
import sys
from collections import OrderedDict


def parse_inventory(path):
    groups = OrderedDict()
    children = {}
    current = "ungrouped"
    section_kind = "hosts"

    with open(path, encoding="utf-8") as fh:
        for lineno, raw in enumerate(fh, 1):
            line = raw.strip()
            if not line or line.startswith(("#", ";")):
                continue

            if line.startswith("[") and line.endswith("]"):
                header = line[1:-1].strip()
                name, _, suffix = header.partition(":")
                current = name
                section_kind = suffix or "hosts"
                if section_kind == "hosts":
                    groups.setdefault(name, [])
                elif section_kind == "children":
                    children.setdefault(name, [])
                    groups.setdefault(name, [])
                # [group:vars] sections hold variables, not hosts
                continue

            entry = line.split()[0]  # drop inline host vars like ansible_host=...
            if section_kind == "hosts":
                groups.setdefault(current, [])
                if entry not in groups[current]:
                    groups[current].append(entry)
            elif section_kind == "children":
                children[current].append(entry)

    return groups, children


def resolve(group, groups, children, seen=None):
    """Return all hosts in a group, including those from child groups."""
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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inventory", nargs="?", default="inventory.ini")
    args = parser.parse_args()

    try:
        groups, children = parse_inventory(args.inventory)
    except OSError as exc:
        sys.exit(f"error: {exc}")

    for group in groups:
        hosts = resolve(group, groups, children)
        if not hosts and group == "ungrouped":
            continue
        print(f"[{group}]")
        for host in hosts:
            print(f"  {host}")
        print()


if __name__ == "__main__":
    main()
```

Run it with:

```
python3 print_inventory_groups.py inventory.ini
```

With your current inventory, it should print:

```
[web]
  web01.example.com
  web02.example.com

[db]
  db01.example.com
```

It also handles a few things your file doesn't use yet:
- **Comments:** lines starting with `#` or `;` are skipped.
- **Host variables:** anything after the host name on the same line (like `web01 ansible_host=10.0.0.1`) is dropped.
- **Ungrouped hosts:** hosts listed before any section header appear under `ungrouped`.
- **Child groups:** a `[parent:children]` section lists the parent group with the hosts from its child groups added in.
- **Variable sections:** `[group:vars]` sections are ignored.

It doesn't expand host ranges like `web[01:10].example.com`. If you need that, or want results that exactly match what Ansible resolves, `ansible-inventory -i inventory.ini --graph` shows the grouping directly.
