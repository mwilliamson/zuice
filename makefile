.PHONY: test upload clean bootstrap setup assert-converted-readme

test:
	_virtualenv/bin/nosetests test

test-all: setup
	_virtualenv/bin/tox
	make clean

upload: setup
	python setup.py sdist upload
	make clean
	
register: setup
	python setup.py register

README: README.md
	pandoc --from=markdown --to=rst README.md > README

clean:
	rm -f README
	rm -f MANIFEST
	rm -rf dist
	cd doc; $(MAKE) clean
	
bootstrap: _virtualenv setup
	_virtualenv/bin/pip install -e .
ifneq ($(wildcard test-requirements.txt),) 
	_virtualenv/bin/pip install -r test-requirements.txt
endif
	make clean

setup: README

_virtualenv: 
	virtualenv _virtualenv
	_virtualenv/bin/pip install 'distribute>=0.6.45'
