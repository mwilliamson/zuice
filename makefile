.PHONY: test

test:
	nosetests test --detailed-errors

checks:
	pyflakes .
