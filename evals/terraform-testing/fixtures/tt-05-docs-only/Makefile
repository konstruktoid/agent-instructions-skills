.PHONY: test
test:
	terraform init -backend=false -input=false
	terraform fmt -check -recursive
	terraform test
