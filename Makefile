.PHONY: help init ship test

.DEFAULT_GOAL = help

help:
	@echo 'make init – installs library locally, along with development dependencies'
	@echo 'make test – runs the test suite'
	@echo 'make ship – ships to pypi'

init:
	pip install -e .[dev]

ship:
	# this probably is only relevant for me, Dan
	python setup.py sdist bdist_wheel && twine upload dist/*

test:
	nosetests --with-coverage --cover-package=csvkitcat
