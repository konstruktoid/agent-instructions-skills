.PHONY: check
check:
	terraform init -backend=false -input=false
	terraform fmt -check -recursive
	terraform validate
