.PHONY: test

test:
	nosetests test

checks:
	pyflakes .

clean:
	find . -name "*.pyc" -exec rm '{}' ';'
	cd doc; $(MAKE) clean
