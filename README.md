# datmo
Open source model tracking tool for developers

Coming March 2018 :) 

## Introduction

As data scientists, machine learning engineers, and deep learning engineers, we faced a number of issues keeping track of our work and maintaining versions that could be put into production quicker. 

In order to solve this challenge, we figured there were a few components we need to put together to make it work. 

1) Source code should be managed with current source control management tools (of which git is the most popular currently) 
2) Dependencies should be encoded in one place for your source code (e.g. requirements.txt in python and pre-built containers) 
3) Large files that cannot be stored in source code like weights files, data files, etc should be stored separately
4) Configurations and hyperparameters that define your experiments (e.g. data split, alpha, beta, etc)
5) Performance metrics that evaluate your model (e.g. validation accuracy)

We realized that we likely won't come up with the best solution on our own and thought it would make most sense to gather feedback from a community of like-minded individuals facing the same issue and develop an open protocol everyone can benefit from. 

## Generate Docs
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

## Installation from Source
```
$ python setup.py clean --all install
```

## Test out CLI
```
$ pytest
```


