I couldn't save the script as a file because the Write tool is disabled in this session. Here is the script, so you can save it as `group_hosts.py`. I haven't run it.

```python
#!/usr/bin/env python3
"""Print the hosts of a static INI inventory grouped by group name."""
import sys


def parse_inventory(path):
    groups = {}
    current = None  # None while inside a :vars or :children section
    with open(path) as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith(("#", ";")):
                continue
            if line.startswith("[") and line.endswith("]"):
                name = line[1:-1]
                if ":" in name:  # [group:vars] / [group:children]
                    current = None
                else:
                    current = name
                    groups.setdefault(current, [])
                continue
            if current is not None:
                # first token is the host; the rest are inline host vars
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

I took "our static inventory file" to mean `inventory.ini` in the repo root, which is the only inventory file there. Run it with `python3 group_hosts.py [path]`. The path is optional and defaults to `inventory.ini`.

For the current file, it should print:

```
web:
  web01.example.com
  web02.example.com
db:
  db01.example.com
```

- **Skipped lines:** it skips blank lines and comments (`#` or `;`).
- **Inline variables:** it keeps only the hostname from a host line and ignores inline variables such as `ansible_host=...`.
- **`[group:vars]` and `[group:children]` sections:** it ignores their contents. A parent group defined only through `:children` therefore doesn't list its child groups' hosts.
- **Host ranges:** it doesn't expand ranges like `web[01:05]`.

If you want the `:children` groups resolved or ranges expanded, tell me and I'll add them. `ansible-inventory --list` would also do this without a custom parser.
