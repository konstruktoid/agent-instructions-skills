I couldn't save the script to disk because the Write tool is disabled in this session. Nothing has been created or run. Here is the script to save as `group_hosts.py`:

```python
#!/usr/bin/env python3
"""Print the hosts of a static INI inventory grouped by group name."""
import sys
from collections import OrderedDict


def parse_inventory(path):
    groups = OrderedDict()
    current = None
    kind = "hosts"
    with open(path, encoding="utf-8") as fh:
        for raw in fh:
            line = raw.split("#", 1)[0].split(";", 1)[0].strip()
            if not line:
                continue
            if line.startswith("[") and line.endswith("]"):
                name, _, suffix = line[1:-1].partition(":")
                current = name
                kind = suffix or "hosts"
                if kind == "hosts":
                    groups.setdefault(current, [])
                continue
            if kind != "hosts":
                continue  # skip [group:vars] and [group:children] entries
            if current is None:
                current = "ungrouped"
                groups.setdefault(current, [])
            groups[current].append(line.split()[0])
    return groups


def main(argv):
    path = argv[1] if len(argv) > 1 else "inventory.ini"
    for group, hosts in parse_inventory(path).items():
        print(f"{group}:")
        for host in hosts:
            print(f"  {host}")


if __name__ == "__main__":
    main(sys.argv)
```

Run it with `python3 group_hosts.py [inventory.ini]`. The path defaults to `inventory.ini`.

I read `inventory.ini`, which has `[web]` with web01 and web02, and `[db]` with db01. From reading the script, the output should be:

```
web:
  web01.example.com
  web02.example.com
db:
  db01.example.com
```

- **Comments:** It ignores `#` and `;` comments.
- **Host variables:** It keeps only the hostname from lines like `host ansible_host=...`.
- **Sections:** It skips `[group:vars]` and `[group:children]` sections.
- **No header:** Hosts that appear before any group header go under `ungrouped`.
- **Not handled:** Ansible range patterns such as `web[01:05]` aren't expanded.

If you enable Write or want me to save it somewhere specific, I can create the file and run it against the inventory.
