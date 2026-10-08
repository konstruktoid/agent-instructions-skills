Puppet and Chef solve the same problem, but they differ in how you write configuration and how it gets applied.

## Language and style

- **Puppet** uses a declarative DSL. You describe the desired end state (`package { 'nginx': ensure => installed }`). Puppet works out the order from dependency relationships you declare (`require`, `before`, `notify`, `->`). The DSL is restrictive on purpose, so manifests are easy to read and hard to make too clever.
- **Chef** uses Ruby directly. Recipes are Ruby files, and resources are Ruby method calls. They run in the order written, from top to bottom. You can use loops, conditionals, and any Ruby gem. That makes Chef more flexible, and it also makes recipes easier to turn into unmaintainable code.

**Practical effect:** Puppet suits teams of sysadmins who want guardrails. Chef suits teams with developers who are comfortable in Ruby.

## Execution model and ordering

- **Puppet** builds a dependency graph. It compiles a catalog on the server, and the agent applies it. Ordering mistakes show up as missing-dependency or cycle errors. Without explicit dependencies, ordering is not guaranteed, but it is deterministic by default.
- **Chef** applies resources in run-list order. This is easier to reason about ("it runs top to bottom"). It also has a two-phase evaluation, compile and then converge. That catches people out when Ruby code runs at compile time and not at converge time.

## Architecture

| | Puppet | Chef |
|---|---|---|
| Default model | Agent/server (pull) | Client/server (pull), or serverless with `chef-solo`/`chef-zero` |
| Catalog | Compiled on the server | Client evaluates cookbooks locally |
| Data lookup | Hiera, with a strong hierarchy | Attributes, data bags, and roles/environments |
| Facts/node data | Facter | Ohai |
| Packaging unit | Modules | Cookbooks |
| Agentless/ad hoc | Puppet Bolt | Chef Workstation tooling (`knife`) |

Puppet's server does more of the work. In Chef, the client does the work, so more logic runs on each node.

## Testing and workflow

- **Puppet:** `puppet-lint`, `rspec-puppet`, and Litmus or Beaker for acceptance tests. The catalog compile lets you check a lot without a real node.
- **Chef:** Test Kitchen, InSpec, and ChefSpec. Test Kitchen's workflow of converging a throwaway VM or container and verifying it with InSpec is well regarded and widely used.

## Ecosystem and community

- **Puppet** has Puppet Forge, a mature module ecosystem, and strong adoption in large and regulated enterprises. Puppet has been owned by Perforce since 2022.
- **Chef** has the Supermarket for cookbooks and a strong compliance story through InSpec. Progress Software has owned Chef since 2020. Parts of the project have moved to a more commercial licensing model.
- Both have lost mindshare to Ansible, Terraform, and Kubernetes-based tooling. Check each project's current licensing and release status before committing, because this has changed over the years.

## Learning curve

- **Puppet:** you have to learn the DSL, the resource model, Hiera, and the dependency system. Once you know them, the code is uniform.
- **Chef:** it is easy if you know Ruby, and harder if you don't. You also need to learn the compile/converge phases, attributes precedence (it has many levels), and the surrounding tools.

## When to pick which

- **Pick Puppet** if you want strict declarative modeling, a central compile step, and consistent code across a large team or a large fleet.
- **Pick Chef** if you want procedural control, a developer-oriented workflow, and the freedom to use full Ruby.
- **Consider neither** for a new project unless you already have staff or code invested. Check whether Ansible or a cloud-native approach covers your needs.

I can go deeper on any of these, such as a side-by-side example of the same task in both tools, or migration paths between them.
