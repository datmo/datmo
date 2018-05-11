# ![Datmo Logo](images/datmo-logo.png)
[![PyPI version](https://badge.fury.io/py/datmo.svg)](https://badge.fury.io/py/datmo)
[![Build Status](https://travis-ci.org/datmo/datmo.svg?branch=master)](https://travis-ci.org/datmo/datmo)
[![Build status](https://ci.appveyor.com/api/projects/status/5302d8a23qr4ui4y/branch/master?svg=true)](https://ci.appveyor.com/project/asampat3090/datmo/branch/master)
[![Coverage Status](https://coveralls.io/repos/github/datmo/datmo/badge.svg?branch=master)](https://coveralls.io/github/datmo/datmo?branch=master)
[![Documentation Status](https://readthedocs.org/projects/datmo/badge/?version=latest)](http://datmo.readthedocs.io/en/latest/?badge=latest)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/853b3d01b4424ac9aa72f9d5fead83b3)](https://www.codacy.com/app/datmo/datmo)

**Datmo** is an open source model tracking and reproducibility tool for developers. Use `datmo init` to turn any repository into a trackable task record with reusable environments and metrics logging.

### Table of Contents
* [Introduction](#introduction)
* [Requirements](#requirements)
* [Installation](#installation)
* [Examples](#examples)
* [Project Templates](#templates)
* [Documentation](#documentation)
* [Contributing to Datmo](/CONTRIBUTING.md)

## Introduction
Tracking experiments in a unified manner for data science, machine learning, and artificial intelligence projects is difficult for many reasons, with one of the largest being the lack of interoperability between frameworks, languages, environments, and best practices.

Datmo's open source tool helps to alleviate some of the largest pain points of dealing with model-based projects by leveraging strong foundational technologies and enforcing a mildly opinionated set of conventions in a framework, language, and platform-agnostic CLI, with additional SDKs for more granular control and workflow integration.

## Requirements

* [openssl](https://github.com/openssl/openssl/blob/master/INSTALL)
* [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
* [docker](https://docs.docker.com/engine/installation/)

## Installation
```
pip install datmo
```

## Project Examples
In the `/examples` folder we have a few scripts you can run to get a feel for datmo. You can 
navigate to [Examples](/examples/README.md) to learn more about how you can run the examples 
and get started with your own projects.

Here's a comparison of a typical logistic regression model with one leveraging Datmo.

<table class="tg">
  <tr>
    <th class="tg-us36">Normal Script</th>
    <th class="tg-us36">With Datmo</th>
  </tr>
<tr>
<td class="tg-us36">
<pre lang="python">
from sklearn import datasets
from sklearn import linear_model as lm
from sklearn import model_selection as ms
from sklearn import externals as ex
#
#
#
#
#
#
iris_dataset = datasets.load_iris()
X = iris_dataset.data
y = iris_dataset.target
data = ms.train_test_split(X, y)
X_train, X_test, y_train, y_test = data
#
model = lm.LogisticRegression(solver="newton-cg")
model.fit(X_train, y_train)
ex.joblib.dump(model, 'model.pkl')
#
train_acc = model.score(X_train, y_train)
test_acc = model.score(X_test, y_test)
#
print(train_acc)
print(test_acc)
#
#
#
#
#
#
#
#
#
</pre></td>
<td class="tg-us36">
<pre lang="python">
from sklearn import datasets
from sklearn import linear_model as lm
from sklearn import model_selection as ms
from sklearn import externals as ex
import datmo # extra line
#
config = {
    "solver": "newton-cg"
} # extra line
#
iris_dataset = datasets.load_iris()
X = iris_dataset.data
y = iris_dataset.target
data = ms.train_test_split(X, y)
X_train, X_test, y_train, y_test = data
#
model = lm.LogisticRegression(**config)
model.fit(X_train, y_train)
ex.joblib.dump(model, "model.pkl")
#
train_acc = model.score(X_train, y_train)
test_acc = model.score(X_test, y_test)
#
stats = {
    "train_accuracy": train_acc,
    "test_accuracy": test_acc
} # extra line
#
datmo.snapshot.create(
    message="my first snapshot",
    filepaths=["model.pkl"],
    config=config,
    stats=stats
) # extra line
</pre></td>
</tr>
</table>

In order to run the above code you can do the following. 

1. Navigate to a directory with a project

        $ mkdir MY_PROJECT
        $ cd MY_PROJECT

2. Initialize a datmo project

        $ datmo init
       
3. Copy the datmo code above into a `train.py` file in your `MY_PROJECT` directory
4. Run the script like you normally would in python 

        $ python train.py
        
5. Congrats! You just created your first snapshot :) Now run an ls command for snapshots to see your first snapshot.

        $ datmo snapshot ls

## Project Templates
In the `/templates` folder we have templates for those who will be starting their projects from scratch. 

Each folder includes a set of files that are not required by datmo but that augment your project and may be useful
as you start new projects. 

## How it works
### Project Structure
When running `datmo init`, Datmo adds a hidden `.datmo` directory which keeps track of all of the various entities at play. This is ncessary to render a repository datmo-enabled. 

### Snapshots

<p align="center">
    The fundamental unit of record in the Datmo ecosystem is a <b>Snapshot</b>, which contains 5 first-class components.
    <br><br>
    <img size="250px" src="https://raw.githubusercontent.com/datmo/datmo/docs-update/images/snapshot-badge-readme.png">
</p>


#### Code
Source code should be managed with current source control management tools. Datmo currently is built on top of git, but could theoretically be ported to work with any similar SCM protocol. While datmo will track all of your local changes and experiments on your machine, you will still need to push changes to a remote repository for them to be continually synced with a manager of choice (like GitHub).

For sharing Datmo entities directly with others (beta), see [this section](#sharing-beta) of the README below.

#### Environment
Dependencies should be encoded using standard best practices for your source code. Python packages should be enumerated in a `requirements.txt` file, while system level dependencies (typically found during GPU workflows) should be written into a `Dockerfile`. 

#### Configuration
Variables used in your experiment that are necessary for reproducibility. These typically include algorithm hyperparameter values, train/test data split, etc.

#### Files
Large files that cannot be stored in source code (ie: untrackable in git due to size) should be stored separately. For data sources that are not discretizable into files (or are stored elsewhere), it is advised to write out the location/directory of these data sources/files as an entry in the `stats` property. 

#### Stats
Model metrics are written to the `stats` property of a snapshot. Datmo does not enforce any type of formal metric definition, the user is free to pass any key-value dictionary during snapshot creation. This enables users to abide by their own metric logging convention while having the flexibility of being able to natively compare metrics across algorithms or frameworks.


## Documentation
The full docs are hosted [here](https://datmo.readthedocs.io/en/latest/index.html). If you wish to contribute to the docs (source code located here in `/docs`), follow the procedure outlined in `CONTRIBUTORS.md`.

## Sharing (Beta)
Although datmo is made to track your changes locally, you can share a project with your
friends by doing the following (this is shown only for git, if you are using another git 
tracking tool, you can likely do something similar). NOTE: If your files are too big or 
cannot be added to SCM then this may not work for you. 
```
$ git add -f .datmo/*
$ git commit -m "my_message"
$ git push 
$ git push origin +refs/datmo/*:refs/datmo/*
```
The above will allow you to share datmo results and entities with yourself or others on 
other machines. NOTE: you will have to remove .datmo/ from tracking to start using datmo
on the other machine. To do that you can use the commands below
```
$ git rm -r --cached
$ git add .
$ git commit -m "removed .datmo from tracking"
```