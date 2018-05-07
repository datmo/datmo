# Developer Tools

## Dev Installation
```
# Clean up pycache and pyc libraries
$ find . | grep -E "(__pycache__|\.pyc$)" | xargs rm -rf

# Install the package and clean up all builds
$ python setup.py clean --all install
```

## Local Documentation Build
```
$ pip install sphinx==1.7.4
$ pip install sphinx-argparse==0.2.2
$ cd docs
$ rm -rf source/*
$ make clean
$ sphinx-build -b html . _build/html # emulates readthedocs build
$ pip install sphinx-rtd-theme
$ pip install recommonmark
```

## Testing
The testing done below emulates what is done in the build on [travis](https://travis-ci.org/datmo/datmo)
```
$ pip install pytest pytest-cov
$ pip install coveralls
$ export TEST_DATMO_DIR="/mydir" # Must be an absolute path
$ export LOGGING_LEVEL=DEBUG # sets logging level to debug for tests
$ python -m pytest --cov-config .coveragerc --cov=datmo
```

## Cleaning Up Code
We use [yapf](https://github.com/google/yapf) to clean code and have added a pre-commit hook to
ensure any changed files adhere to the styles specified in `.style.yapf` in the root of the project. 

```
# Run on all files 
$ yapf -i `git ls-files | grep -F .py`
```

```
# Run on changed files prior to commit, see travis-ci/pre-commit
CHANGED_FILES=`git diff --cached --name-only | grep .py`
if [ -z $CHANGED_FILES ]
then
    echo "No Python Files Changed"
else
    echo $CHANGED_FILES
    yapf -i $CHANGED_FILES
    git diff --name-only --cached | xargs -l git add
fi
```

## Upload to PyPi
Versions of datmo are uploaded to [PyPI](https://pypi.org/project/datmo/) with the following steps
1) Ensure the `VERSION` file in the `datmo/` module is updated to the desired version to upload 
(must be later than the previous version on PyPI based on semver)
2) Run the following commands

        $ rm -rf dist/
        $ python setup.py bdist_wheel
        $ twine upload dist/*