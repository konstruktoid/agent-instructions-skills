I couldn't save the script as a file. The Write tool is disabled in this session, so I haven't created or run anything. Here is the script. Save it as `group_hosts.py` next to `inventory.ini`:

```python
#!/usr/bin/env python3
"""Print the hosts in a static INI inventory grouped by group name."""
import sys


def parse_inventory(path):
    groups = {}
    current = None
    skip = False  # inside a [group:vars] or [group:children] section
    with open(path, encoding="utf-8") as fh:
        for raw in fh:
            line = raw.strip()
            if not line or line.startswith(("#", ";")):
                continue
            if line.startswith("[") and line.endswith("]"):
                name = line[1:-1]
                skip = ":" in name
                current = None if skip else name
                if current is not None:
                    groups.setdefault(current, [])
                continue
            if skip or current is None:
                continue
            # first token is the host; the rest are inline vars (ansible_host=...)
            groups[current].append(line.split()[0])
    return groups


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "inventory.ini"
    for group, hosts in parse_inventory(path).items():
        print(f"{group}:")
        for host in hosts:
            print(f"  {host}")


if __name__ == "__main__":
    main()
```

Run it with `python3 group_hosts.py [path/to/inventory.ini]`. The path defaults to `inventory.ini`.

Given your current `inventory.ini`, it should print:

```
web:
  web01.example.com
  web02.example.com
db:
  db01.example.com
```

- **What it skips:** `#` and `;` comments, blank lines, and `[group:vars]` and `[group:children]` sections.
- **Inline host vars:** a line like `web01 ansible_host=10.0.0.1` is reported as just `web01`.
- **Not handled:** nested groups through `:children`, and host ranges such as `web[01:05]`.

If you'd like me to write it to disk, enable the Write tool or tell me another way to save it, and I'll also run it against your inventory.
