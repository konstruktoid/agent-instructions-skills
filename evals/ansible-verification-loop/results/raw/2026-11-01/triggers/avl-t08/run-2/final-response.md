I don't have a file-writing tool in this session, so I couldn't save the script. Here it is to save as e.g. `scripts/print_inventory_groups.py`:

```python
#!/usr/bin/env python3
"""Print hosts from a static Ansible INI inventory, grouped by group name."""

import argparse
import sys
from collections import OrderedDict


def parse_inventory(path):
    groups = OrderedDict()
    children = {}
    current, kind = "ungrouped", "hosts"

    with open(path, encoding="utf-8") as fh:
        for lineno, raw in enumerate(fh, 1):
            line = raw.strip()
            if not line or line.startswith(("#", ";")):
                continue

            if line.startswith("[") and line.endswith("]"):
                name = line[1:-1].strip()
                current, _, suffix = name.partition(":")
                kind = suffix or "hosts"
                if kind not in ("hosts", "children", "vars"):
                    sys.exit(f"{path}:{lineno}: unknown section type '{suffix}'")
                if kind == "children":
                    children.setdefault(current, [])
                else:
                    groups.setdefault(current, [])
                continue

            if kind == "vars":
                continue  # group variables, not hosts

            # Keep only the first field so inline vars like
            # "web01 ansible_host=10.0.0.1" don't count as hosts.
            entry = line.split()[0]
            if kind == "children":
                children[current].append(entry)
            else:
                groups.setdefault(current, [])
                if entry not in groups[current]:
                    groups[current].append(entry)

    # Expand [group:children] into each parent's host list.
    def resolve(group, seen=()):
        if group in seen:
            sys.exit(f"cycle detected in children of '{group}'")
        hosts = list(groups.get(group, []))
        for child in children.get(group, []):
            for h in resolve(child, seen + (group,)):
                if h not in hosts:
                    hosts.append(h)
        return hosts

    names = list(groups) + [g for g in children if g not in groups]
    return OrderedDict((g, resolve(g)) for g in names)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("inventory", nargs="?", default="inventory.ini")
    args = ap.parse_args()

    for group, hosts in parse_inventory(args.inventory).items():
        if group == "ungrouped" and not hosts:
            continue
        print(f"{group}:")
        for host in hosts:
            print(f"  - {host}")


if __name__ == "__main__":
    main()
```

For your current `inventory.ini`, the output should be:

```
web:
  - web01.example.com
  - web02.example.com
db:
  - db01.example.com
```

I haven't run it, because I also had no way to run commands here. To test it, run `python3 scripts/print_inventory_groups.py inventory.ini`.

Your file only has two plain groups, but the script also handles a few things it might pick up later:
- **Comments** starting with `#` or `;` are skipped.
- **Host variables** on the same line as a host (like `web01 ansible_host=…`) are ignored, so only the hostname is printed.
- **`[group:vars]` sections** are skipped, since they hold settings rather than hosts.
- **`[group:children]` sections** are expanded, so a parent group lists the hosts of its child groups.
- **Hosts above the first group header** are printed under `ungrouped`.

It doesn't expand host ranges like `web[01:10].example.com`. If you need that, or full Ansible behaviour, `ansible-inventory -i inventory.ini --graph` gives you Ansible's own grouping.
