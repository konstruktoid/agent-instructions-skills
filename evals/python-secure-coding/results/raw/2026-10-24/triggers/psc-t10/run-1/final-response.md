I couldn't find a JSON file to format. This workspace has no `*.json` files at all. The config files it does have are YAML (`docker-compose.yml`, `k8s/deployment.yml`, `.gitlab-ci.yml`, `.github/workflows/deploy.yml`, the Ansible `roles/nginx/*/main.yml`), plus `inventory.ini` and `infra/main.tf`.

Which file did you mean? You can:
- give me the path, if the file is outside this workspace,
- paste the JSON here, and I'll send it back formatted with the keys sorted, or
- tell me to do it to one of the YAML files above instead.

I'll sort keys at every level of nesting and leave the order of array items alone, unless you want something different.
