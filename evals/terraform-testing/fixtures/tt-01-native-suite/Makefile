.PHONY: test integration
test:
	terraform init -backend=false -input=false
	terraform fmt -check -recursive
	terraform test -test-directory=tests/unit

integration:
	terraform init -backend=false -input=false
	terraform test -test-directory=tests/integration
