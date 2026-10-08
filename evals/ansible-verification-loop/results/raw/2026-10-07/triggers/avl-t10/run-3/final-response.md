# Puppet vs. Chef: Practical Differences

## Core philosophy

- **Puppet is declarative and model-driven.** You describe the desired end state ("package X installed, service Y running") in a DSL. Puppet builds a dependency graph and decides the order of operations.
- **Chef is imperative-leaning and code-driven.** Recipes are plain Ruby, executed top to bottom in the order you write them. Resources are declarative, but ordering and control flow are yours to manage.

## Language and learning curve

| | Puppet | Chef |
|---|---|---|
| Language | Puppet DSL (Ruby-like, but restricted) | Ruby with a Chef DSL |
| Ordering | Dependency graph (`require`, `before`, `notify`) | Sequential by default, in run-list order |
| Flexibility | Limited; the DSL deliberately constrains you | Very high; full Ruby available |
| Learning curve | Easier for sysadmins with no programming background | Easier for developers; steeper for ops-only teams |

Practical consequence: Puppet code is more uniform and easier to audit. Chef code can do more, but it can also get more tangled.

## Architecture

- **Puppet:** Agent/server (`puppetserver`) is the common model. Agents pull catalogs, compiled server-side from manifests and facts (via Facter). Masterless `puppet apply` is also supported.
- **Chef:** Chef Infra Client runs on nodes and pulls from a Chef Infra Server. Chef Solo or `chef-client --local-mode` (Zero) is available for masterless use. Ohai provides node facts.

In both, the default is pull-based on a roughly 30-minute interval, so drift is corrected automatically.

## Code organization

- **Puppet:** Modules containing manifests, templates (ERB/EPP), and files. Node classification via `site.pp`, an ENC, or Hiera. **Hiera** is the standard data/code separation layer.
- **Chef:** Cookbooks containing recipes, attributes, templates, and resources. Roles, environments, and data bags (or policyfiles) assign configuration. **Policyfiles** are the modern recommended workflow over roles/environments.

## Testing and workflow

- **Puppet:** `puppet-lint`, `rspec-puppet`, and Litmus or Beaker for acceptance tests. `puppet parser validate` and `--noop` give quick checks.
- **Chef:** Cookstyle (linting), ChefSpec (unit), and Test Kitchen with InSpec (integration). Test Kitchen is well regarded for spinning up real instances to converge and verify.

## Ecosystem and licensing

- **Puppet:** Puppet Forge for modules. Now owned by Perforce. The open source version has become more restricted, and a community fork, **OpenVox**, exists.
- **Chef:** Chef Supermarket for cookbooks. Now owned by Progress. Distribution and licensing for Chef Infra binaries require acceptance of a commercial license, and a community-maintained fork, **Cinc**, provides free builds.

Check the current licensing terms for either tool before committing, since they have changed in recent years.

## Practical tradeoffs

**Puppet tends to fit when:**
- You want strong guardrails and consistent, reviewable code across a large team.
- Compliance and reporting (drift, what changed) are priorities.
- Your team is ops-focused.

**Chef tends to fit when:**
- Your team is comfortable with Ruby and wants to write real logic (loops, conditionals, custom resources).
- You want a developer-style workflow with strong integration testing.
- Complex, procedural deployment steps matter.

## Common pain points

- **Puppet:** Dependency ordering errors and cycles can be confusing. Compiling catalogs on the server can be a scaling bottleneck. Upgrades between major versions have been bumpy.
- **Chef:** Ordering is easy to reason about, but the two-phase execution (compile vs. converge) trips up newcomers. Cookbook dependency management and server upkeep add overhead.

## Bottom line

Both solve the same problem with similar resource abstractions (package, file, service, template). The deciding factors are usually team skills (ops vs. developer), how much control versus consistency you want, and licensing and support. If you're starting fresh today, also consider agentless tools like Ansible, which avoid agents and servers entirely. Many teams have moved toward them for simpler needs.
