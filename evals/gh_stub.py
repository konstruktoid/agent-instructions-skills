#!/usr/bin/env python3
"""Stand in for the `gh` CLI during an eval run, serving GitHub state from a local JSON file.

The GitHub skills teach behavior that only shows against a live API: reading every page of a
list, reading a write back because some fields are accepted and ignored, and proposing rather than
applying an outward-facing change. No eval run may touch a real organization, so the harness puts
this script on PATH as `gh` and points `GH_STUB_DIR` at a directory holding `state.json`.

`state.json` holds:

- `resources`: REST paths, without a leading slash, mapped to their JSON value. A key may carry a
  query string, such as `orgs/acme/members?filter=2fa_disabled`, to serve a filtered list. A list
  value is paginated; an object with `list_key` and `items` is a list wrapped the way
  `environments` and `installations` are.
- `ignored_fields`: per resource path, dotted field names a write accepts, echoes in its response,
  and does not store.
- `default_repo`, `user`, and `per_page`, the page size used when a request names none.

A PUT to a ruleset replaces it whole, as GitHub does, so a body carrying one changed field drops
every rule; a PUT anywhere else merges into the stored object.

Every invocation is appended to `log.jsonl` beside the state, which is what the graders read.
Anything this script does not model fails with a message saying the command is unavailable here,
rather than imitating a GitHub error.
"""

from __future__ import annotations

import fcntl
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlsplit

DEFAULT_PER_PAGE = 30
RULESET_LIST_LIMIT = 30
LIST_SUMMARY_DROP = ("rules", "conditions", "bypass_actors")
ITEM_KEYS = ("id", "login", "name", "property_name", "slug", "key")


class StubError(Exception):
    """A request the stub answers with a failure, carrying gh's exit status."""

    def __init__(self, message: str, status: int = 1) -> None:
        """Keep the message for stderr and the exit status for the caller."""
        super().__init__(message)
        self.status = status


def stub_dir() -> Path:
    """Return the directory holding this run's state and log."""
    value = os.environ.get("GH_STUB_DIR")
    if not value:
        message = "gh: GH_STUB_DIR is not set; this command is not available in this environment"
        raise StubError(message)
    return Path(value)


def load_state(directory: Path) -> dict[str, Any]:
    """Read the state file."""
    return json.loads((directory / "state.json").read_text(encoding="utf-8"))


def save_state(directory: Path, state: dict[str, Any]) -> None:
    """Write the state file back."""
    text = json.dumps(state, indent=2, sort_keys=True) + "\n"
    (directory / "state.json").write_text(text, encoding="utf-8")


def log_call(directory: Path, entry: dict[str, Any]) -> None:
    """Append one invocation to the log the graders read."""
    with (directory / "log.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, sort_keys=True) + "\n")


def run_jq(expression: str, document: str) -> str:
    """Filter one JSON document with the system jq, printing strings raw as `gh --jq` does."""
    jq = shutil.which("jq")
    if jq is None:
        message = "gh: --jq needs jq, which is not available in this environment"
        raise StubError(message)
    # A fixed argument list, shell=False; the expression is the caller's own jq program.
    completed = subprocess.run(  # noqa: S603
        [jq, "-r", expression],
        input=document,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise StubError(completed.stderr.strip() or "gh: jq failed", completed.returncode)
    return completed.stdout


def split_path(raw: str, state: dict[str, Any]) -> tuple[str, dict[str, str]]:
    """Normalize a request path and return it with its query parameters."""
    owner, _, repo = str(state.get("default_repo", "")).partition("/")
    raw = raw.replace("{owner}", owner).replace("{repo}", repo)
    parts = urlsplit(raw)
    path = parts.path.removeprefix("https://api.github.com").strip("/")
    return path, dict(parse_qsl(parts.query))


def resource_key(path: str, query: dict[str, str]) -> str:
    """Return the state key for a path, including any filter that is not a paging parameter."""
    filters = sorted(
        (name, value) for name, value in query.items() if name not in {"page", "per_page"}
    )
    if not filters:
        return path
    return path + "?" + "&".join(f"{name}={value}" for name, value in filters)


def find(state: dict[str, Any], path: str, query: dict[str, str]) -> tuple[str, Any, Any]:
    """Locate a resource: return (container key, value, item key), raising 404 when absent.

    A path ending in an item's id, login, or name inside a stored list resolves to that item,
    with the list's key and the item's position.
    """
    resources = state["resources"]
    for key in (resource_key(path, query), path):
        if key in resources:
            return key, resources[key], None
    parent, _, leaf = path.rpartition("/")
    items = list_of(resources.get(parent))
    if items is not None:
        for index, item in enumerate(items):
            if isinstance(item, dict) and any(str(item.get(k)) == leaf for k in ITEM_KEYS):
                return parent, item, index
    message = "gh: Not Found (HTTP 404)"
    raise StubError(message)


def list_of(value: object) -> list[Any] | None:
    """Return the items of a stored list, wrapped or not, or None for any other value."""
    items = value.get("items") if isinstance(value, dict) and "list_key" in value else value
    return items if isinstance(items, list) else None


def page_size(query: dict[str, str], state: dict[str, Any]) -> int:
    """Return the page size a request asked for, or the state's default."""
    return int(query.get("per_page") or state.get("per_page") or DEFAULT_PER_PAGE)


def page_of(value: object, query: dict[str, str], state: dict[str, Any], page: int) -> object:
    """Return one page of a list value, or the value itself when it is not a list."""
    items = list_of(value)
    if items is None:
        return value
    size = page_size(query, state)
    chunk = items[(page - 1) * size : page * size]
    if isinstance(value, dict):
        return {"total_count": len(items), value["list_key"]: chunk}
    return chunk


def page_count(value: object, query: dict[str, str], state: dict[str, Any]) -> int:
    """Return how many pages a list value spans."""
    items = list_of(value)
    return 1 if items is None else max(1, -(-len(items) // page_size(query, state)))


def summarize(path: str, page: object) -> object:
    """Drop the detail fields a ruleset list response omits."""
    if path.endswith("/rulesets") and isinstance(page, list):
        return [{k: v for k, v in item.items() if k not in LIST_SUMMARY_DROP} for item in page]
    return page


def typed(raw: str) -> object:
    """Convert an `-F` value the way gh does: literals, integers, and `@file` contents."""
    literals = {"true": True, "false": False, "null": None}
    if raw in literals:
        return literals[raw]
    if raw.lstrip("-").isdigit():
        return int(raw)
    if raw.startswith("@"):
        source = raw[1:]
        return sys.stdin.read() if source == "-" else Path(source).read_text(encoding="utf-8")
    return raw


def set_field(body: dict[str, Any], name: str, value: object) -> None:
    """Assign one field, honoring gh's `a[b]=` nesting and `a[]=` list append."""
    head, _, rest = name.partition("[")
    keys = [head] + [part.rstrip("]") for part in rest.split("[")] if rest else [head]
    target: Any = body
    for index, key in enumerate(keys):
        last = index == len(keys) - 1
        if key == "":
            target.append(value)
            return
        if last:
            target[key] = value
            return
        default: Any = [] if keys[index + 1] == "" else {}
        target = target.setdefault(key, default)


def merge(target: dict[str, Any], patch: dict[str, Any], ignored: set[str], prefix: str) -> None:
    """Deep-merge a request body into a stored object, skipping the ignored dotted fields."""
    for key, value in patch.items():
        dotted = f"{prefix}{key}"
        if dotted in ignored:
            continue
        if isinstance(value, dict) and isinstance(target.get(key), dict):
            merge(target[key], value, ignored, dotted + ".")
        else:
            target[key] = value


def write(state: dict[str, Any], method: str, path: str, body: dict[str, Any]) -> object:
    """Apply one write to the state and return the response body."""
    resources = state["resources"]
    ignored = set(state.get("ignored_fields", {}).get(path, []))
    items = list_of(resources.get(path))
    if method == "POST" and items is not None:
        numbers = [item["id"] for item in items if isinstance(item.get("id"), int)]
        created = {"id": max(numbers, default=1000) + 1, **body}
        items.append(created)
        return created
    if method == "PUT" and path not in resources:
        parent, _, leaf = path.rpartition("/")
        siblings = list_of(resources.get(parent))
        if siblings is not None and not any(
            isinstance(item, dict) and any(str(item.get(k)) == leaf for k in ITEM_KEYS)
            for item in siblings
        ):
            siblings.append({"login": leaf, **body})
            return None
        if siblings is None:
            resources[path] = {}
    key, value, index = find(state, path, {})
    if method == "DELETE":
        if index is None:
            del resources[key]
        else:
            (list_of(resources[key]) or []).pop(index)
        return None
    if not isinstance(value, dict):
        message = f"gh: {method} on a list is not available in this environment"
        raise StubError(message)
    if method == "PUT" and "/rulesets/" in f"/{path}":
        kept = {name: value[name] for name in ("id",) if name in value}
        value.clear()
        value.update(kept)
    merge(value, body, ignored, "")
    echoed = json.loads(json.dumps(value))
    merge(echoed, body, set(), "")
    return echoed


@dataclass
class ApiRequest:
    """The parts of one `gh api` invocation the stub acts on."""

    endpoint: str = ""
    method: str = ""
    body: dict[str, Any] = field(default_factory=dict)
    jq: str = ""
    flags: set[str] = field(default_factory=set)


VALUE_FLAGS = {"-H", "--header", "--hostname", "--cache", "-p", "--preview"}
SWITCHES = {"--paginate", "--slurp", "--silent", "-i", "--include", "--verbose"}


def read_input(source: str) -> dict[str, Any]:
    """Read an `--input` body from a file or from stdin."""
    text = sys.stdin.read() if source == "-" else Path(source).read_text(encoding="utf-8")
    return json.loads(text)


def parse_api(args: list[str]) -> ApiRequest:
    """Parse `gh api` arguments, failing on any flag the stub does not model."""
    request = ApiRequest()
    position = 0
    while position < len(args):
        arg = args[position]
        value = args[position + 1] if position + 1 < len(args) else ""
        step = 2
        if arg in {"-X", "--method"}:
            request.method = value.upper()
        elif arg in {"-f", "--raw-field", "-F", "--field"}:
            name, _, raw = value.partition("=")
            set_field(request.body, name, raw if arg in {"-f", "--raw-field"} else typed(raw))
        elif arg == "--input":
            request.body.update(read_input(value))
        elif arg in {"-q", "--jq"}:
            request.jq = value
        elif arg in SWITCHES:
            request.flags.add("--include" if arg == "-i" else arg)
            step = 1
        elif arg in VALUE_FLAGS:
            pass
        elif arg.startswith("-"):
            message = f"gh api: flag {arg} is not available in this environment"
            raise StubError(message)
        else:
            request.endpoint, step = arg, 1
        position += step
    request.method = request.method or ("POST" if request.body else "GET")
    return request


def check_request(request: ApiRequest) -> None:
    """Reject the request shapes gh itself rejects, and the GraphQL endpoint the stub lacks."""
    if not request.endpoint or request.endpoint == "graphql":
        message = "gh api: only REST endpoints are available in this environment"
        raise StubError(message)
    if "--slurp" in request.flags and request.jq:
        message = "the `--slurp` option is not supported with `--jq` or `--template`"
        raise StubError(message)


def render(pages: list[object], request: ApiRequest) -> str:
    """Format response pages the way gh prints them."""
    if "--silent" in request.flags:
        return ""
    if "--slurp" in request.flags:
        merged: list[object] = []
        for page in pages:
            merged.extend(page if isinstance(page, list) else [page])
        pages = [merged]
    chunks = []
    for page in pages:
        document = json.dumps(page, indent=2)
        chunks.append(run_jq(request.jq, document) if request.jq else document + "\n")
    header = "HTTP/2.0 200 OK\n\n" if "--include" in request.flags else ""
    return header + "".join(chunks)


def api(args: list[str], state: dict[str, Any], entry: dict[str, Any]) -> tuple[str, bool]:
    """Answer `gh api`, returning the output and whether the state changed."""
    request = parse_api(args)
    check_request(request)
    path, query = split_path(request.endpoint, state)
    entry.update({"method": request.method, "path": path, "query": query, "body": request.body})
    if request.method != "GET":
        response = write(state, request.method, path, request.body)
        pages: list[object] = [] if response is None else [response]
        changed = True
    else:
        _, value, _ = find(state, path, query)
        first = int(query.get("page") or 1)
        last = page_count(value, query, state) if "--paginate" in request.flags else first
        pages = [summarize(path, page_of(value, query, state, n)) for n in range(first, last + 1)]
        changed = False
    entry["pages"] = len(pages)
    return render(pages, request), changed


def option(args: list[str], *names: str) -> str:
    """Return the value of the first named option present, or an empty string."""
    for index, arg in enumerate(args):
        for name in names:
            if arg == name and index + 1 < len(args):
                return args[index + 1]
            if arg.startswith(name + "="):
                return arg.split("=", 1)[1]
    return ""


def rulesets_for(state: dict[str, Any], args: list[str]) -> tuple[str, list[dict[str, Any]]]:
    """Return the ruleset path and list a `gh ruleset` command addresses."""
    org = option(args, "-o", "--org")
    repo = option(args, "-R", "--repo") or str(state.get("default_repo", ""))
    path = f"orgs/{org}/rulesets" if org else f"repos/{repo}/rulesets"
    rulesets = state["resources"].get(path)
    if not isinstance(rulesets, list):
        message = "gh: Not Found (HTTP 404)"
        raise StubError(message)
    return path, rulesets


def ruleset(args: list[str], state: dict[str, Any], entry: dict[str, Any]) -> str:
    """Answer `gh ruleset list`, `view`, and `check`."""
    if not args:
        message = "gh ruleset: a subcommand is required"
        raise StubError(message)
    sub, rest = args[0], args[1:]
    entry["subcommand"] = sub
    if sub == "list":
        _, rulesets = rulesets_for(state, rest)
        limit = int(option(rest, "-L", "--limit") or RULESET_LIST_LIMIT)
        shown = rulesets[:limit]
        lines = [f"Showing {len(shown)} of {len(rulesets)} rulesets", "", "ID\tNAME\tSTATUS"]
        lines += [f"{item['id']}\t{item['name']}\t{item['enforcement']}" for item in shown]
        return "\n".join(lines) + "\n"
    if sub == "view":
        _, rulesets = rulesets_for(state, rest)
        wanted = next((arg for arg in rest if arg.isdigit()), "")
        for item in rulesets:
            if str(item["id"]) == wanted:
                return json.dumps(item, indent=2) + "\n"
        message = "gh: Not Found (HTTP 404)"
        raise StubError(message)
    if sub == "check":
        path, rulesets = rulesets_for(state, rest)
        repo = state["resources"].get(path.removesuffix("/rulesets"), {})
        default = repo.get("default_branch", "main")
        positional = [arg for arg in rest if not arg.startswith("-")]
        flagged = {option(rest, flag) for flag in ("-R", "--repo")}
        names = [arg for arg in positional if arg not in flagged]
        branch = default if "--default" in rest else (names[0] if names else "main")
        entry["branch"] = branch
        refs = {f"refs/heads/{branch}", "~ALL"} | (
            {"~DEFAULT_BRANCH"} if branch == default else set()
        )
        rules = []
        for item in rulesets:
            include = item.get("conditions", {}).get("ref_name", {}).get("include", [])
            if item.get("enforcement") == "active" and refs & set(include):
                rules += [
                    f"- {rule['type']} (from {item['name']})" for rule in item.get("rules", [])
                ]
        heading = f"{len(rules)} rules apply to branch {branch} in repo {repo.get('full_name', '')}"
        return "\n".join([heading, *rules]) + "\n"
    message = f"gh ruleset {sub}: not available in this environment"
    raise StubError(message)


def repo(args: list[str], state: dict[str, Any], entry: dict[str, Any]) -> tuple[str, bool]:
    """Answer `gh repo view` and the security flags of `gh repo edit`."""
    sub, rest = (args[0], args[1:]) if args else ("", [])
    entry["subcommand"] = sub
    name = next((arg for arg in rest if "/" in arg and not arg.startswith("-")), "")
    path = f"repos/{name or state.get('default_repo', '')}"
    _, value, _ = find(state, path, {})
    if sub == "view":
        fields = {
            "nameWithOwner": value.get("full_name"),
            "visibility": str(value.get("visibility", "")).upper(),
            "isPrivate": value.get("private"),
            "defaultBranchRef": {"name": value.get("default_branch")},
        }
        selected = option(rest, "--json")
        document = json.dumps(
            {k: fields.get(k) for k in selected.split(",")} if selected else value
        )
        expression = option(rest, "-q", "--jq")
        return (run_jq(expression, document) if expression else document + "\n"), False
    if sub == "edit":
        body: dict[str, Any] = {}
        visibility = option(rest, "--visibility")
        if visibility:
            body.update({"visibility": visibility, "private": visibility != "public"})
        flags = {
            "--enable-secret-scanning": "secret_scanning",
            "--enable-secret-scanning-push-protection": "secret_scanning_push_protection",
            "--enable-advanced-security": "advanced_security",
        }
        for flag, field in flags.items():
            if flag in rest:
                body.setdefault("security_and_analysis", {})[field] = {"status": "enabled"}
        entry.update({"method": "PATCH", "path": path, "body": body})
        write(state, "PATCH", path, body)
        return "", True
    message = f"gh repo {sub}: not available in this environment"
    raise StubError(message)


def dispatch(args: list[str], state: dict[str, Any], entry: dict[str, Any]) -> tuple[str, bool]:
    """Route one invocation to the command it names."""
    command, rest = (args[0], args[1:]) if args else ("", [])
    entry["command"] = command
    if command == "api":
        return api(rest, state, entry)
    if command == "ruleset":
        return ruleset(rest, state, entry), False
    if command == "repo":
        return repo(rest, state, entry)
    if command == "auth" and rest[:1] == ["status"]:
        user = state.get("user", "eval-admin")
        return f"github.com\n  ✓ Logged in to github.com account {user}\n", False
    message = f"gh {command}: not available in this environment"
    raise StubError(message)


def main(argv: list[str]) -> int:
    """Run one gh invocation against the stub state and log it."""
    try:
        directory = stub_dir()
    except StubError as exc:
        print(exc, file=sys.stderr)
        return exc.status
    with (directory / "state.lock").open("w", encoding="utf-8") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        state = load_state(directory)
        entry: dict[str, Any] = {"argv": argv}
        try:
            output, changed = dispatch(argv, state, entry)
        except StubError as exc:
            entry.update({"status": exc.status, "error": str(exc)})
            log_call(directory, entry)
            print(exc, file=sys.stderr)
            return exc.status
        except (OSError, ValueError) as exc:
            entry.update({"status": 1, "error": str(exc)})
            log_call(directory, entry)
            print(f"gh: {exc}", file=sys.stderr)
            return 1
        if changed:
            save_state(directory, state)
        entry["status"] = 0
        log_call(directory, entry)
    sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
