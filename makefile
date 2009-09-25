.PHONY: test

test:
	nosetests test

checks:
	pyflakes .
