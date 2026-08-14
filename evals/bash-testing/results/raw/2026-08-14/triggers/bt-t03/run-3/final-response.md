There's no bash script performing input validation in this workspace — `scripts/backup.sh` is the only shell script, and it takes no arguments or user input to validate (it uses hardcoded paths). The other files are Go, Python, Terraform, Ansible, and CI configs, none of which is an "input validation script" in Bash.

Could you point me to the specific script you mean, or is `scripts/backup.sh` actually the target (in which case it would first need argument/input handling added before I can test rejection paths)?
