# Deserialization

Read this when the change loads a serialized object, parses YAML or XML, or accepts a
structured document from a network source, an upload, or a cache.

## Pickle and friends

- Never unpickle (`pickle`, `marshal`, `shelve`) data from an untrusted or network
  source (`S301`). Deserializing a pickle executes arbitrary code by design; no amount
  of validation after the fact makes it safe.
- If a pickle-shaped interface is required across a trust boundary, replace it with a
  data-only format (JSON, or a schema-validated message) rather than trying to filter
  the pickle stream.

## YAML

- Use `yaml.safe_load`, or `Loader=yaml.SafeLoader`. Never `yaml.load` or `yaml.Loader`
  on untrusted YAML (`S506`).
- The unsafe loaders instantiate arbitrary Python objects from tags in the document.

## XML

- Use `defusedxml` instead of the stdlib `xml` modules when parsing untrusted XML, to
  avoid entity-expansion (billion laughs) and XXE attacks.
- The stdlib parsers resolve external entities and expand nested entities by default in
  several configurations, which turns a small document into a denial of service or a
  local file read.

## Trust boundary check

The question a linter cannot answer is where the data came from. Trace the input back to
its origin before deciding a loader is safe. A file on disk is untrusted if an
unprivileged process, an upload handler, or a previous run of a network-facing service
could have written it.
