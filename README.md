\
# ![Datmo Logo](images/datmo-logo.png)
[![PyPI version](https://badge.fury.io/py/datmo.svg)](https://badge.fury.io/py/datmo)
[![Coverage Status](https://coveralls.io/repos/github/datmo/datmo/badge.svg?branch=master)](https://coveralls.io/github/datmo/datmo?branch=master)
[![Documentation Status](https://readthedocs.org/projects/datmo/badge/?version=latest)](http://datmo.readthedocs.io/en/latest/?badge=latest)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/853b3d01b4424ac9aa72f9d5fead83b3)](https://www.codacy.com/app/datmo/datmo)

| OS | CI testing on `master` |
|----|--------------------|
| <img height="20" src="http://icons.iconarchive.com/icons/dakirby309/simply-styled/256/OS-Linux-icon.png"> | [![Linux](https://travis-ci.org/datmo/datmo.svg?branch=master)](https://travis-ci.org/datmo/datmo) |
| <img height="20" src="http://icons.iconarchive.com/icons/icons8/windows-8/128/Systems-Mac-Os-icon.png"> | [![CircleCI branch](https://circleci.com/gh/datmo/datmo.svg?style=shield)](https://circleci.com/gh/datmo/datmo) |
| <img height="20" src="http://icons.iconarchive.com/icons/dakirby309/windows-8-metro/128/Folders-OS-Windows-8-Metro-icon.png"> | [![Windows](https://ci.appveyor.com/api/projects/status/5302d8a23qr4ui4y/branch/master?svg=true)](https://ci.appveyor.com/project/asampat3090/datmo/branch/master) |

# Datmo Alpha Release

**Datmo** is an open source model tracking and reproducibility tool for developers. Use `datmo init` to turn any repository into a trackable task record with reusable environments and metrics logging.


**Note**: The current version of Datmo is an alpha release. This means commands are subject to change. If you find any bugs please
feel free contribute by adding issues so the contributors can address them.  



## Features

- **One command environment setup** (languages, frameworks, packages, etc)
- **Tracking and logging** for model config and results
- **Project versioning** (model state tracking)
- **Experiment reproducibility** (re-run tasks)
- **Visualize + export** experiment history

---

### Table of Contents
* [Requirements](#requirements)
* [Installation](#installation)
* [Examples](#examples)
* [Documentation](#documentation)
* [Transform a Current Project](#transform)
* [Sharing](#sharing)
* [Contributing to Datmo](/CONTRIBUTING.md)

## Requirements

* [openssl](https://github.com/openssl/openssl/blob/master/INSTALL)
* [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
* [docker](https://docs.docker.com/engine/installation/)

## Installation
```
pip install datmo
```

## Examples
In the `/examples` folder we have a few scripts you can run to get a feel for datmo. You can 
navigate to [Examples](/examples/README.md) to learn more about how you can run the examples 
and get started with your own projects.

For more advanced tutorials, check out our dedicated tutorial repository [here](https://github.com/datmo/datmo-tutorials).

Here's a comparison of a typical logistic regression model with one leveraging Datmo.

<table class="tg">
  <tr>
    <th class="tg-us36">Normal Script</th>
    <th class="tg-us36">With Datmo</th>
  </tr>
<tr>
<td class="tg-us36">
<pre lang="python">
# train.py
#
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
# train.py
#
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
        

## How it works
### Project Structure
When running `datmo init`, Datmo adds a hidden `.datmo` directory which keeps track of all of the various entities at play. This is ncessary to render a repository datmo-enabled. 

### Snapshots

<p align="center">
    The fundamental unit of record in the Datmo ecosystem is a <b>Snapshot</b>, which contains 5 first-class components.
    <br><br>
    <img size="250px" src="https://github.com/datmo/datmo/blob/master/images/snapshot-badge-readme.png">
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
The full docs are hosted [here](https://datmo.readthedocs.io/en/latest/index.html). If you wish to contribute to the docs (source code located here in `/docs`), follow the procedure outlined in `CONTRIBUTING.md`.

## Transform a Current Project
You can transform your existing repository into a datmo enabled repository with the following command
```
$ datmo init
```
If at any point you would like to remove datmo you can just remove the `.datmo` directory from your repository
or you can run the following command
```
$ datmo cleanup
```
### Optional: Mark your GitHub repository as a Datmo project
Once you initialize your project, you can denote your repository as a datmo project by adding the following badge to your README file.
This helps someone pulling the code to know how to setup and run Datmo commands, as the badge will link them to usage instructions here.

#### Markdown
```markdown
[![Datmo Model](https://github.com/datmo/datmo/blob/master/images/badge.svg)](https://github.com/datmo/datmo)
```
#### ReStructuredText
```
.. image:: https://github.com/datmo/datmo/blob/master/images/badge.svg
    :target: https://github.com/datmo/datmo
```

## Sharing (Workaround)
**DISCLAIMER:** This is not currently an officially supported option and only works for 
file-based storage layers (as set in the configuration) as a workaround to share datmo projects. 

Although datmo is made to track changes locally, you can share a project by pushing to a remote 
server by doing the following (this is shown only for git, if you are using another SCM 
tracking tool, you can likely do something similar). If your files are too big or 
cannot be added to SCM then this may not work for you. 

The below has been tested on BASH terminals only. If you are using another terminal, you 
may run into some errors. 

### Push to remote
```
$ git add -f .datmo/*  # add in .datmo to your scm
$ git commit -m "adding .datmo to tracking"  # commit it to your scm
$ git push  # push to remote
$ git push origin +refs/datmo/*:refs/datmo/*  # push datmo refs to remote
```
The above will allow you to share datmo results and entities with yourself or others on 
other machines. NOTE: you will have to remove .datmo/ from tracking to start using datmo
on the other machine or another location. See the instructions below to see how to replicate
it at another location

### Pull from remote
```
$ git clone YOUR_REMOTE_URL
$ cd YOUR_REPO 
$ echo '.datmo/*' > .git/info/exclude  # include .datmo into your .git exclude
$ git rm -r --cached .datmo  # remove cached versions of .datmo from scm
$ git commit -m "removed .datmo from tracking"  # clean up your scm so datmo can work 
$ git pull origin +refs/datmo/*:refs/datmo/*  # pull datmo refs from remote
$ datmo init  # This enables datmo in the new location. If you enter blanks, no project information will be updated
```
If you are interested in sharing using the datmo protocol, you can visit [Datmo's website](https://datmo.com/product)
