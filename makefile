.PHONY: test

test:
	nosetests test --with-isolation

checks:
	pyflakes .
