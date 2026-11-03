Both tools are mature, agent-based configuration management systems that came out of the same era. In practice they differ in the language you write, how they run, and who tends to find them comfortable.

## 1. Language and mental model

**Puppet** uses its own **declarative DSL**. You describe the end state, and Puppet builds a dependency graph to reach it.

```puppet
package { 'nginx': ensure => installed }
service { 'nginx':
  ensure  => running,
  enable  => true,
  require => Package['nginx'],
}
```

- Ordering comes from explicit relationships (`require`, `before`, `notify`, `->`), not from the order in the file.
- The language is deliberately limited. That makes it easier for ops-focused people to read, but complex logic can get awkward.

**Chef** uses a **Ruby-based DSL**. Recipes are real Ruby code.

```ruby
package 'nginx'
service 'nginx' do
  action [:enable, :start]
end
```

- Resources run **in the order you write them**, which is easier to reason about for many people.
- You have the full power of Ruby: loops, libraries and custom logic. That is flexible, but it makes it easy to write code that isn't idempotent or is hard to maintain.

**In practice:** Puppet suits teams that want guardrails and a strictly declarative model. Chef suits teams comfortable writing code who want imperative control.

## 2. How a run works

| | Puppet | Chef |
|---|---|---|
| Server | Puppet Server (JVM) compiles a **catalog** for each node | Chef Infra Server stores cookbooks and node data. The **client** does the compiling |
| Where logic runs | Mostly on the server, so nodes receive a pre-built catalog | On the node, which downloads cookbooks and runs them |
| Agent mode | Pull model, every 30 min by default | Pull model, on a configurable interval |
| Serverless option | `puppet apply` | `chef-client --local-mode` / Chef Zero / Chef Solo |
| Two-phase behavior | Compile catalog, then apply | Compile phase, then converge phase. The difference between `compile_time` and converge time is a classic Chef gotcha |

Because Puppet compiles on the server, the server sees more load and nodes have less to do. Because Chef compiles on the client, nodes can run arbitrary Ruby, which is more flexible but makes each node do more work.

## 3. Data and node information

- **Puppet:** **Facter** gathers facts about each node, and **Hiera** provides hierarchical data lookup (per environment, OS, role and so on). Hiera is one of Puppet's strongest features for keeping data separate from code.
- **Chef:** **Ohai** gathers node data, and data comes from **attributes** (with a precedence system that can be confusing), **data bags**, and roles/environments or **Policyfiles**.

## 4. Code organization and ecosystem

- **Puppet:** modules, with the **roles and profiles** pattern as the standard architecture. Modules come from the **Puppet Forge**, and r10k or Code Manager handle deploying environments.
- **Chef:** cookbooks, wrapper cookbooks and Policyfiles. Cookbooks come from the **Chef Supermarket**, and Berkshelf (now mostly replaced by Policyfiles) handles dependencies.

## 5. Testing

- **Puppet:** rspec-puppet for unit tests, Litmus or Beaker for acceptance tests, and PDK for scaffolding and linting.
- **Chef:** ChefSpec for unit tests, **Test Kitchen** for integration tests, and **InSpec** for compliance testing. Test Kitchen and InSpec are widely regarded as excellent, and InSpec is used even outside Chef.

## 6. Reporting and drift

- Puppet's agent reports each resource change, and Puppet Enterprise has strong reporting and dashboards for drift and compliance. Puppet has historically been strong at **continuous enforcement** at large scale.
- Chef provides similar functionality through Chef Automate, often paired with InSpec for compliance.

## 7. Vendor and community situation

- **Puppet** is owned by Perforce. In late 2024 Perforce moved official binaries and packages behind commercial terms, which led to the community fork **OpenVox** (under Vox Pupuli). Check this licensing and distribution situation if you're starting fresh.
- **Chef** is owned by Progress. The commercial products are licensed, and the community distribution **Cinc** provides free builds.
- Both have seen market share shift toward **Ansible** (agentless, YAML) and toward immutable or container-based approaches.

## Rules of thumb

- **Pick Puppet** if you have a large, long-lived server fleet, want strict declarative state with strong drift enforcement, and have a team that prefers configuration over code.
- **Pick Chef** if your team is developer-heavy and comfortable with Ruby, you need complex logic in your configs, or you value the Test Kitchen and InSpec workflow.
- **Consider neither** for new projects that are mostly ephemeral or cloud-native. Ansible, image baking with Packer, or Kubernetes-native tooling may fit better.

If it would help, I can map either tool's concepts to Ansible equivalents.
