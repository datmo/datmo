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
$ pip install sphinx-argparse
$ cd docs
$ rm -rf source/*
$ make clean
$ sphinx-apidoc -o source/ ../datmo ../datmo/core ../datmo/tests ../datmo/cli/command ../datmo/cli/driver
$ ln -s ../examples/README.md examples.md
$ make html
$ pip install sphinx-rtd-theme
$ pip install recommonmark
```

## Testing
```
$ pip install pytest pytest-cov
$ pip install coveralls
$ export TEST_DATMO_DIR="/mydir" # Must be an absolute path
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