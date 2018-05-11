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

## Converting files to RST
We use a mixture of markdown and rst files throughout the repo depending 
on which works best. We will eventually just work with one, but for the timebeing
the following command can be run to convert any markdown file to rst.
```
$ pandoc --from=markdown --to=rst --output=MY_FILE.rst MY_FILE.md
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

If you run into issues with testing on docker, you might want to clean up your open docker containers 
with the following command
```
$ docker rm -f $(docker ps -a -q)
```

## Cleaning Up Code
We use [yapf](https://github.com/google/yapf) to clean code and have added a check in the build to 
ensure any changed files adhere to the styles specified in `.style.yapf` in the root of the project. 
The build will fail if the files don't match the style. 

We have included some basic commands you can use on the repo after your changes, however, we suggest
that you create a pre-commit hook in your git project so that you can ensure every commit is clean 
and prevent any broken builds from formatting issues. You can refer to the [documentation on the yapf 
github repo](https://github.com/google/yapf/tree/master/plugins) for instructions on how to set this up.

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

If you're using Visual Studio Code and want to run `yapf -i [filename]` on save,  install the [Run on Save] extension.(https://marketplace.visualstudio.com/items?itemName=emeraldwalk.RunOnSave)

```json
"emeraldwalk.runonsave": {
  "commands": [
    {
      "match":"\\.py$",
      "cmd":"yapf -i ${file}"
    }
  ]
}
```

## Upload to PyPi
Versions of datmo are uploaded to [PyPI](https://pypi.org/project/datmo/) with the following steps. NOTE:
only those with credentials for the PyPI website will be able to upload new versions. 

1) Ensure the `VERSION` file in the `datmo/` module is updated to the desired version to upload 
(must be later than the previous version on PyPI based on semver)
2) Run the following commands

        $ rm -rf dist/
        $ python setup.py bdist_wheel
        $ twine upload dist/*