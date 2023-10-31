# json-fg-validator

[![Build Status](https://github.com/tomkralidis/json-fg-validator/workflows/build%20%E2%9A%99%EF%B8%8F/badge.svg)](https://github.com/wmo-im/json-fg-validator/actions)

# OGC Features and Geometries JSON - Part 1: Core Test Suite

json-fg-validator provides validation capabilities for [OGC Features and Geometries JSON - Part 1: Core](https://github.com/opengeospatial/ogc-feat-geo-json).

## Installation

### pip

Install latest stable version from [PyPI](https://pypi.org/project/json-fg-validator).

```bash
pip3 install json-fg-validator
```

### From source

Install latest development version.

```bash
python3 -m venv json-fg-validator
cd json-fg-validator
. bin/activate
git clone https://github.com/tomkralidis/json-fg-validator.git
cd json-fg-validator
pip3 install -r requirements.txt
python3 setup.py install
```

## Running

From command line:
```bash
# fetch version
json-fg-validator --version

# sync supporting configuration bundle (schemas, topics, etc.)
json-fg-validator bundle sync

# abstract test suite

# validate WCMP 2 metadata against abstract test suite (file on disk)
json-fg-validator ets validate /path/to/file.json

# validate WCMP 2 metadata against abstract test suite (URL)
json-fg-validator ets validate https://example.org/path/to/file.json

# validate WCMP 2 metadata against abstract test suite (URL), but turn JSON Schema validation off
json-fg-validator ets validate https://example.org/path/to/file.json --no-fail-on-schema-validation

# adjust debugging messages (CRITICAL, ERROR, WARNING, INFO, DEBUG) to stdout
json-fg-validator ets validate https://example.org/path/to/file.json --verbosity DEBUG

# write results to logfile
json-fg-validator ets validate https://example.org/path/to/file.json --verbosity DEBUG --logfile /tmp/foo.txt
```

## Using the API
```pycon
>>> # test a file on disk
>>> import json
>>> from json_fg_validator.ets import ets
>>> 
>>> with open('/path/to/file.json')) as fh:
...     data = json.load(fh)
>>> # test ETS
>>> ts = ets.JSONFGTestSuite2(datal)
>>> ts.run_tests()  # raises ValueError error stack on exception
>>> # test a URL
>>> from urllib2 import urlopen
>>> from StringIO import StringIO
>>> content = StringIO(urlopen('https://....').read())
>>> data = json.loads(content)
>>> ts = ets.JSONFGTestSuite2(data)
>>> ts.run_tests()  # raises ValueError error stack on exception
>>> # handle json_fg_validator.errors.TestSuiteError
>>> # json_fg_validator.errors.TestSuiteError.errors is a list of errors
>>> try:
...    ts.run_tests()
... except json_fg_validator.errors.TestSuiteError as err:
...    print('\n'.join(err.errors))
>>> ...
```

## Development

```bash
python3 -m venv json-fg-validator
cd json-fg-validator
source bin/activate
git clone https://github.com/tomkralidis/json-fg-validator.git
pip3 install -r requirements.txt
pip3 install -r requirements-dev.txt
python3 setup.py install
```

### Running tests

```bash
# via setuptools
python3 setup.py test
# manually
python3 tests/run_tests.py
```

## Releasing

```bash
# create release (x.y.z is the release version)
vi json_fg_validator/__init__.py  # update __version__
git commit -am 'update release version x.y.z'
git push origin master
git tag -a x.y.z -m 'tagging release version x.y.z'
git push --tags

# upload to PyPI
rm -fr build dist *.egg-info
python3 setup.py sdist bdist_wheel --universal
twine upload dist/*

# publish release on GitHub (https://github.com/tomkralidis/json-fg-validator/releases/new)

# bump version back to dev
vi json_fg_validator/__init__.py  # update __version__
git commit -am 'back to dev'
git push origin master
```

## Code Conventions

[PEP8](https://www.python.org/dev/peps/pep-0008)

## Issues

Issues are managed at https://github.com/tomkralidis/json-fg-validator/issues

## Contact

* [Tom Kralidis](https://github.com/tomkralidis)
