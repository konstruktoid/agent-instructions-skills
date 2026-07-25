# YAML Quoting and Scalar Resolution

Read this when a change adds, removes, or argues about quoting in a YAML file, or when
explaining to a reviewer why a particular value must stay quoted.

## Authoritative source

The [YAML 1.2.2 Specification](https://yaml.org/spec/1.2.2/) is the authoritative
reference for scalar resolution, quoting, and tag semantics.

## Why values need quoting

Use the specification to explain *why* a value needs quoting, for example:

- The "Norway problem": unquoted `no`, `yes`, `on`, `off`, `y`, and `n` resolve to
  booleans rather than the strings they appear to be.
- Numbers with leading zeros or embedded colons resolve to octal or sexagesimal values
  rather than the literal string.

## Relationship to the repository's linters

Ansible's YAML loader and `ansible-lint`'s default `yaml`/`truthy` rule already reject
unquoted truthy values other than `true`/`false`, so the specification reinforces
existing lint behavior rather than replacing it.

Never use the specification to justify removing existing quoting, the `---`
document-start marker, or any other convention that `ansible-lint` or `yamllint`
already enforces in the target repository. The repository's configured linters win.
