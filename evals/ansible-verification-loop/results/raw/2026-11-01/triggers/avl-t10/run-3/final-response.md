Puppet and Chef both keep servers in a desired state. They differ mainly in how you write configuration and how the system runs.

## 1. How you write configuration

**Puppet** uses its own declarative language (Puppet DSL). You describe the end state, and Puppet works out the order using the dependency graph.
```puppet
package { 'nginx': ensure => installed }
service { 'nginx':
  ensure  => running,
  require => Package['nginx'],
}
```

**Chef** uses a Ruby DSL. Resources are still declarative, but recipes are real Ruby and run in the order written.
```ruby
package 'nginx'
service 'nginx' do
  action [:enable, :start]
end
```

**What this means in practice:**
- Puppet is easier for ops staff who don't program. It's also harder to write clever, messy code in it.
- Chef is more flexible because you get loops, libraries and full Ruby. That suits teams with developers, but cookbooks can turn into hard-to-maintain programs.
- Chef runs top to bottom, which many people find easier to reason about. Puppet's graph-based ordering surprises newcomers unless they set dependencies explicitly with `require`, `before`, `notify`, and so on.

## 2. Architecture and workflow

| | Puppet | Chef |
|---|---|---|
| Model | Agent pulls a compiled catalog from Puppet Server (or `puppet apply` with no server) | Chef Client pulls cookbooks from Chef Infra Server (or Chef Zero / Solo with no server) |
| Where code is compiled | On the server, into a catalog per node | On the node, which runs the Ruby itself |
| Node data | Facter facts, PuppetDB | Ohai attributes, the Chef Server search index |
| Default run interval | 30 min | 30 min (often set via cron or a service) |
| Ad-hoc orchestration | Bolt | Chef has `knife ssh` but is weaker here; teams often add other tools |

Compiling on the server, as Puppet does, gives you a central record of exactly what each node should be and keeps secrets logic off the nodes, but the server has to do more work as you scale. Compiling on the node, as Chef does, spreads that work out, but the node needs the full cookbook and the Ruby runtime.

## 3. Data and code organization

- **Puppet:** modules, Hiera for hierarchical data (per-environment, per-role or per-node values), and the roles-and-profiles pattern. Hiera is a real strength for keeping data separate from code.
- **Chef:** cookbooks, roles, environments, data bags and Policyfiles. Attribute precedence has many levels (default, normal, override, automatic and others) and is a common source of confusion. Policyfiles fix much of this by pinning exact cookbook versions per role.

## 4. Testing and tooling

- **Chef** has long had a strong testing culture: ChefSpec for unit tests, Test Kitchen for VM or container integration tests, and InSpec (now Chef InSpec) for compliance and verification. InSpec is widely used even outside Chef.
- **Puppet** has rspec-puppet, puppet-lint, the PDK (Puppet Development Kit) and Litmus for acceptance tests. They're solid, but the community uses them less consistently.

## 5. Ecosystem and vendor situation

- **Puppet** is owned by Perforce. In 2024–2025 Perforce moved official binaries and packages behind commercial terms, and the community responded with **OpenVox**, an open-source fork. If you're starting fresh, check licensing and which distribution you'll use.
- **Chef** is owned by Progress. The commercial versions need a license, and **Cinc** is the community rebuild of the open-source code. Progress's attention has moved more toward compliance and InSpec than core config management.
- Both have smaller communities than they did around 2015. Much of the new greenfield work has gone to Ansible (agentless, YAML) or to immutable infrastructure (images plus Terraform or Kubernetes).

## 6. Rough guidance

**Puppet tends to fit when:**
- you have a large, long-lived server fleet and want strict, auditable desired state
- the team is mostly ops, not developers
- you want a central compiled catalog and reporting through PuppetDB

**Chef tends to fit when:**
- the team is comfortable with Ruby and wants programming flexibility
- you value its testing workflow (Test Kitchen, InSpec)
- you already use Chef's compliance tools

**Consider neither when** you want agentless, push-based runs with little setup. Ansible usually fits that better, especially for smaller fleets or orchestration-heavy work.

If you have a particular environment in mind, such as fleet size, OS mix or team skills, I can make this more specific.
