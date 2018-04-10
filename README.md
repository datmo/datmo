# Datmo
[![Build Status](https://travis-ci.org/datmo/datmo.svg?branch=master)](https://travis-ci.org/datmo/datmo)
[![Coverage Status](https://coveralls.io/repos/github/datmo/datmo/badge.svg?branch=master)](https://coveralls.io/github/datmo/datmo?branch=master)
[![Documentation Status](https://readthedocs.org/projects/datmo/badge/?version=latest)](http://datmo.readthedocs.io/en/latest/?badge=latest)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/853b3d01b4424ac9aa72f9d5fead83b3)](https://www.codacy.com/app/datmo/datmo)

Open source model tracking tool for developers. Use `datmo init` to turn any repository into a supercharged experiment tracking 
powerhouse.

### Table of Contents
* [Introduction](#introduction)
* [Requirements](#requirements)
* [Installation](#installation)
* [Documentation](#documentation)
* [Testing](#testing)

## Introduction

As data scientists, machine learning engineers, and deep learning engineers, we faced a number of issues keeping track of our work and maintaining versions that could be put into production quicker. 

In order to solve this challenge, we figured there were a few components we need to put together to make it work. 

1) Source code should be managed with current source control management tools (of which git is the most popular currently) 
2) Dependencies should be encoded in one place for your source code (e.g. requirements.txt in python and pre-built containers) 
3) Large files that cannot be stored in source code like weights files, data files, etc should be stored separately
4) Configurations and hyperparameters that define your experiments (e.g. data split, alpha, beta, etc)
5) Performance metrics that evaluate your model (e.g. validation accuracy)

We realized that we likely won't come up with the best solution on our own and thought it would make most sense to gather feedback from a community of like-minded individuals facing the same issue and develop an open protocol everyone can benefit from. 

## Requirements

* [openssl](https://github.com/openssl/openssl/blob/master/INSTALL)
* [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
* [docker](https://docs.docker.com/engine/installation/)

## Installation
```
# Clean up pycache and pyc libraries
$ find . | grep -E "(__pycache__|\.pyc$)" | xargs rm -rf

# Install the package and clean up all builds
$ python setup.py clean --all install
```

## Documentation
```
$ pip install sphinx-argparse
$ cd docs
$ rm -rf source/*
$ make clean
$ sphinx-apidoc -o source/ ../datmo
$ make html
$ pip install sphinx-rtd-theme
$ pip install recommonmark
```

## Testing
```
$ pip install pytest pytest-cov
$ pip install coveralls
$ python -m pytest --cov-config .coveragerc --cov=datmo
```

## Project Structure
Datmo adds 2 things to existing repositories to keep track of the work, a `datmo.json` file with settings
associated with the project and a `.datmo` directory which keeps track of all of the various entities. 

## Project Templates
In the `/templates` folder we have templates for those who will be starting their projects from scratch. 

Each folder includes a set of files that are not required by datmo but that augment your project and may be useful
as you start new projects. 

## Project Examples
In the `/examples` folder we have a few projects that have already been created and converted to datmo. You can 
navigate to them and try datmo commands for yourself in order to get a feel for the tool.

