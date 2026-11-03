Puppet and Chef solve the same problem: they keep servers in a declared state, usually with agents pulling config from a central server. In practice they feel quite different to use.

## Language and mental model

**Puppet** uses its own declarative DSL. You describe the end state, and Puppet builds a dependency graph and works out the order to apply it.
```puppet
package { 'nginx': ensure => installed }
service { 'nginx':
  ensure  => running,
  require => Package['nginx'],
}
```
- **Good:** it's easy to read for ops people who don't write code, it pushes you toward idempotent models, and the order is explicit.
- **Bad:** the DSL has limits. Complex logic gets awkward, and when the dependency graph goes wrong (cycles, missing `require`) it can be confusing to debug.

**Chef** uses a Ruby DSL. Recipes are real Ruby code, and resources run in the order they're written. Ruby is available everywhere in the recipe.
```ruby
package 'nginx'
service 'nginx' do
  action [:enable, :start]
end
```
- **Good:** it's very flexible, top-to-bottom order is easy to follow, and developers feel at home.
- **Bad:** it's easy to write imperative code that isn't idempotent. Chef's two-phase run (compile, then converge) catches newcomers out, and you need Ruby skills.

**In short:** Puppet suits ops-heavy teams that want guardrails. Chef suits teams with strong developers who want full programming power.

## Architecture

| | Puppet | Chef |
|---|---|---|
| Central server | Puppet Server (JVM) and PuppetDB | Chef Infra Server (Erlang/Ruby/Postgres stack) |
| Where config is compiled | **On the server.** The agent receives a compiled catalog | **On the node.** chef-client downloads cookbooks and runs them locally |
| Workstation tooling | `puppet` CLI, PDK | Chef Workstation (`knife`, `chef`) |
| Serverless mode | `puppet apply` | `chef-solo` / Chef Zero (local mode) |
| Default agent interval | 30 min | 30 min (configurable) |

The compile location matters most in practice. Puppet's server-side compilation puts the load on the server, and nodes only see their own catalog, which is a security advantage. Chef pushes that work to the nodes, so the server is lighter, but every node gets the cookbook code.

## Data and node information

- **Puppet:** facts come from **Facter**. Data is split from code with **Hiera**, a hierarchical YAML lookup (per environment, OS, role, node, etc.). Hiera is one of Puppet's strongest features.
- **Chef:** facts come from **Ohai**. Data lives in **attributes** with a complex precedence system (default/normal/override/automatic × cookbook/role/environment), plus **data bags** and Policyfiles. The attribute precedence rules are a well-known source of confusion.

## Code organisation and ecosystem

- **Puppet:** modules on **Puppet Forge**. The common pattern is "roles and profiles", and **r10k / Code Manager** handle environment deployment from Git.
- **Chef:** cookbooks on **Chef Supermarket**. **Policyfiles** (the modern approach) or the older roles/environments with Berkshelf.

## Testing

- **Puppet:** rspec-puppet for catalog unit tests, Litmus or Beaker for acceptance tests, PDK for scaffolding and validation.
- **Chef:** ChefSpec for unit tests, **Test Kitchen** + **InSpec** for integration and compliance testing. Chef's testing story is generally seen as the more polished of the two, and InSpec became popular on its own for compliance-as-code.

## Ownership and licensing (worth checking before committing)

- **Puppet:** owned by Perforce. In late 2024 Perforce moved the official builds and packages to a commercial/restricted model. The community responded with **OpenVox**, an open fork. For new deployments, check which distribution you'll actually use.
- **Chef:** owned by Progress since 2020. Commercial use of Chef's official binaries requires a license. **Cinc** is the community-built, freely redistributable distribution.

## Market position

Both are mature and both are losing ground for new projects. Agentless, push-based tools (mainly Ansible), immutable infrastructure (images built with Packer, containers, Kubernetes) and Terraform for provisioning have taken much of their space. Both are still common in large, long-lived fleets, especially in enterprises and regulated environments where continuous drift correction and reporting matter.

## Rough guidance

- **Choose Puppet** if your team is mostly ops, you want a strongly declarative model, you'll use Hiera heavily for data, or you need strong reporting and drift enforcement across a large fleet.
- **Choose Chef** if your team is comfortable with Ruby, you need complex logic in your config, or you value Test Kitchen and InSpec for testing and compliance.
- **Consider neither** if your infrastructure is mostly short-lived servers or containers, or if a push-based agentless tool like Ansible fits how you work. Ansible is usually simpler to adopt for new projects today.
