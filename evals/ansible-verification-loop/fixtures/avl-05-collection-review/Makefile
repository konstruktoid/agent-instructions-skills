.PHONY: lint test

lint:
	ansible-lint .

test: lint
	molecule test -s default
