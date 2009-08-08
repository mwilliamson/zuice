.PHONY: test

test:
	nosetests test --with-isolation --detailed-errors

checks:
	pyflakes .
