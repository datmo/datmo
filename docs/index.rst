Welcome to Datmo's documentation!
=================================

Datmo is an open source model tracking tool for developers

Why we built this
-----------------

As data scientists, machine learning engineers, and deep learning engineers, we faced a number of issues keeping track of our work and maintaining versions that could be put into production quicker.

In order to solve this challenge, we found there are a few components that are critical to ensuring this is the case.

1) Source code should be managed with current source control management tools (of which git is the most popular currently)
2) Dependencies should be encoded in one place for your source code (e.g. requirements.txt in python and pre-built containers)
3) Large files that cannot be stored in source code like weights files, data files, etc should be stored separately
4) Configurations and hyperparameters that define your experiments (e.g. data split, alpha, beta, etc)
5) Performance metrics that evaluate your model (e.g. validation accuracy)

We've encapsulated these concepts in an object called a *snapshot*. A snapshot is a combination of all 5 of the above components
and is the way that Datmo versions models for reproducibility and deployability. Our open source tool is an interface for
developers to transform their current model projects into trackable models that can be used for transportability throughout the
model building process.

We have used this internally to speed up our own iteration processes and are excited to share it with the community to continue
improving. If you're interested in contributing check out `the guidelines <https://github.com/datmo/datmo/blob/master/CONTRIBUTING.md>`_.


Table of contents
-----------------
.. toctree::
    :maxdepth: 3

    cli
    python_sdk
    examples


Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


.. image:: https://badge.fury.io/py/datmo.svg
    :target: https://badge.fury.io/py/datmo
.. image:: https://travis-ci.org/datmo/datmo.svg?branch=master
    :target: https://travis-ci.org/datmo/datmo
.. image:: https://coveralls.io/repos/github/datmo/datmo/badge.svg
    :target: https://coveralls.io/github/datmo/datmo
