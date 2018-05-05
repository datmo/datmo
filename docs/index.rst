Welcome to Datmo's documentation!
=================================

Datmo is an open source model tracking tool for developers

Why we built this
-----------------

As data scientists, machine learning engineers, and deep learning engineers, we faced a number of issues keeping track of our work and maintaining versions that could be put into production quicker.

In order to solve this challenge, we figured there were a few components we need to put together to make it work.

1) Source code should be managed with current source control management tools (of which git is the most popular currently)
2) Dependencies should be encoded in one place for your source code (e.g. requirements.txt in python and pre-built containers)
3) Large files that cannot be stored in source code like weights files, data files, etc should be stored separately
4) Configurations and hyperparameters that define your experiments (e.g. data split, alpha, beta, etc)
5) Performance metrics that evaluate your model (e.g. validation accuracy)

We realized that we likely won't come up with the best solution on our own and thought it would make most sense to gather feedback from a community of like-minded individuals facing the same issue and develop an open protocol everyone can benefit from.


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
