# ![Datmo Logo](images/datmo-logo.png)
[![PyPI version](https://badge.fury.io/py/datmo.svg)](https://badge.fury.io/py/datmo)
[![Coverage Status](https://coveralls.io/repos/github/datmo/datmo/badge.svg?branch=master)](https://coveralls.io/github/datmo/datmo?branch=master)
[![Documentation Status](https://readthedocs.org/projects/datmo/badge/?version=latest)](http://datmo.readthedocs.io/en/latest/?badge=latest)

# Datmo 

**Datmo** is an open source production model management tool for data scientists. Use `datmo init` to turn any repository into a trackable experiment record. Sync using your own cloud.


**Note**: The current version of Datmo is an alpha release. This means commands are subject to change and more features will be added. If you find any bugs please
feel free contribute by adding issues so the contributors can address them.  



## Features

- **One command environment setup** (languages, frameworks, packages, etc)
- **Tracking and logging** for model config and results
- **Project versioning** (model state tracking)
- **Experiment reproducibility** (re-run tasks)
- **Visualize + export** experiment history
- **(coming soon) Dashboards** to visualize experiments


| Feature  | Commands|
| ------------- | ---------------------------- |
| Initializing a Project | `$ datmo init` |
| Setup a new environment | `$ datmo environment setup` |
| Run an experiment | `$ datmo run "python filename.py"` |
| Reproduce a previous experiment | `$ datmo ls` (Find the desired ID) <br> `$ datmo rerun EXPERIMENT_ID` |
| Open a workspace |   `$ datmo notebook`  (Jupyter Notebook) <br> `$ datmo jupyterlab` (JupyterLab) <br> `$ datmo rstudio` (RStudio) <br> `$ datmo terminal` (Terminal)|
| Record your project state <br> (Files, code, env, config, stats) |   `$ datmo snapshot create -m "My first snapshot!"` |
| Switch to a previous project state | `$ datmo snapshot ls` (Find the desired ID) <br> `$ datmo snapshot checkout SNAPSHOT_ID` |
| Visualize project entities | `$ datmo ls` (Experiments) <br> `$ datmo snapshot ls` (Snapshots) <br> `$ datmo environment ls` (Environments) |

---

### Table of Contents
* [Requirements](#requirements)
* [Installation](#installation)
* [Hello World](#hello-world)
* [Examples](#examples)
* [Documentation](#documentation)
* [Transform a Current Project](#transform-a-current-project)
* [Sharing](#sharing-workaround)
* [Contributing to Datmo](/CONTRIBUTING.md)

## Installation

   ### Requirements:  <br />    
   docker (installed and running before starting) : Instructions for [Ubuntu](https://docs.docker.com/install/linux/docker-ce/ubuntu/#uninstall-old-versions), [MacOS](https://docs.docker.com/docker-for-mac/install/#install-and-run-docker-for-mac), [Windows](https://docs.docker.com/docker-for-windows/install/)                 
    
    $ pip install datmo

## Hello-World
Our hello world guide includes showing environment setup and changes, as well as experiment reproducibility. It's available [in our docs here](https://datmo.readthedocs.io/en/latest/quickstart.html).

## Examples
In the `/examples` folder we have a few scripts you can run to get a feel for datmo. You can 
navigate to [Examples](/examples/README.md) to learn more about how you can run the examples 
and get started with your own projects.

For more advanced tutorials, check out our dedicated tutorial repository [here](https://github.com/datmo/datmo-tutorials).


### Environment Setup

Setting up an environment is extremely easy in datmo. Simply respond with `y` when asked about environment setup during initialization, or use `datmo environment setup` at any point. Then follow the resulting prompts. 

<p align="center">
    One example is shown below, for setting up a Python 2.7 TensorFlow with CPU reqs/drivers.
    <br><br>
    <img src="/images/env-setup.gif">
</p>

For the full guide on setting up your environment with datmo, see this page in our documentation [here](https://datmo.readthedocs.io/en/latest/env-setup.html).


### Opening a workspace

After getting your environment setup, most data scientists want to open what we call a workspace (IDE or Notebook programming environment)

<p align="center">
    One example is shown below, for quickly opening a Jupyter Notebook and showing the import of TensorFlow working as intended.
    <br><br>
    <img src="/images/datmo-notebook.gif">
</p>


### Experiment Running and Tracking

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

### Environments, Snapshots, and Runs
See our [concepts page](https://datmo.readthedocs.io/en/latest/concepts.html) in the documentation to see how the moving parts work together in datmo.

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

## Running Tests

Datmo uses pytest for testing. To run the full test suite:

```
$ python -m pytest
```

### Running Tests Without Docker

Some tests require a running Docker daemon. If you don't have Docker installed or running, you can skip these tests by setting the `DATMO_SKIP_DOCKER_TESTS` environment variable:

```
$ DATMO_SKIP_DOCKER_TESTS=1 python -m pytest
```

This will skip all tests that depend on Docker, allowing the test suite to run successfully without a Docker environment.

# FAQs

Q: What  do I do if the `datmo stop --all` doesn't work and I cannot start a new container due to port reallocation?  
A: This could be caused by a ghost container running from another datmo project or another container.  Either you can create a docker image with a specific port allocation (other than 8888),  find the docker image, stop it, and remove it using `docker ps --all` and `docker conntainer stop <ID>` and `docker container rm <ID>`. Or you can stop and remove all images running on the machine [NOTE: This may  affect other docker processes on  your machine so PROCEED WITH CAUTION] `docker container stop $(docker ps  -a -q)` and `docker container rm $(docker ps  -a -q)`
