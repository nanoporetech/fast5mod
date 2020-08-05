OS := $(shell uname)
ifeq ($(OS), Darwin)
SEDI=sed -i '.bak'
else
SEDI=sed -i
endif

PYTHON ?= python3

venv: venv/bin/activate
IN_VENV=. ./venv/bin/activate

venv/bin/activate:
	test -d venv || virtualenv venv --python=$(PYTHON) --prompt "(fast5mod) "
	${IN_VENV} && pip install pip --upgrade


.PHONY: install
install: venv
	${IN_VENV} && pip install -r requirements.txt
	${IN_VENV} && python setup.py install


.PHONY: test
test: install
	${IN_VENV} && pip install pytest pytest-cov flake8 flake8-rst-docstrings flake8-docstrings flake8-import-order
	${IN_VENV} && flake8 fast5mod --import-order-style google --application-import-names fast5mod,libfast5mod

.PHONY: clean
clean:
	(${IN_VENV} && python setup.py clean) || echo "Failed to run setup.py clean"
	rm -rf venv build dist/ *.egg-info/ __pycache__
	find . -name '*.pyc' -delete

.PHONY: build
build: pypi_build/bin/activate
IN_BUILD=. ./pypi_build/bin/activate
pypi_build/bin/activate:
	test -d pypi_build || virtualenv pypi_build --python=python3 --prompt "(pypi) "
	${IN_BUILD} && pip install pip --upgrade
	${IN_BUILD} && pip install --upgrade pip setuptools twine wheel readme_renderer[md]

.PHONY: wheels
wheels:
	docker run -v `pwd`:/io quay.io/pypa/manylinux1_x86_64 /io/build-wheels.sh /io 5 6

.PHONY: sdist
sdist: pypi_build/bin/activate 
	${IN_BUILD} && python setup.py sdist
