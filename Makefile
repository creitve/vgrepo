build: clean check
		pip install wheel
		python setup.py sdist bdist_wheel

check:
		tox -e pep8

publish: build
		pip install twine
		twine upload dist/*

clean:
		rm -rf dist/ build/ *egg-info

.PHONY: check clean package publish
