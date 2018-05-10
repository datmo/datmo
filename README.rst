Datmo
=====

|PyPI version| |Build Status| |Build status| |Coverage Status|
|Documentation Status| |Codacy Badge|

Open source model tracking tool for developers. Use ``datmo init`` to
turn any repository into a supercharged experiment tracking powerhouse.

Table of Contents
~~~~~~~~~~~~~~~~~

-  `Introduction <#introduction>`__
-  `Requirements <#requirements>`__
-  `Installation <#installation>`__
-  `Contributing to Datmo </CONTRIBUTING.md>`__
-  `Testing <#testing>`__

Introduction
------------

As data scientists, machine learning engineers, and deep learning
engineers, we faced a number of issues keeping track of our work and
maintaining versions that could be put into production quicker.

In order to solve this challenge, we found there were a few components
we need to put together to make it work.

1) Source code should be managed with current source control management
   tools (of which git is the most popular currently)
2) Dependencies should be encoded in one place for your source code
   (e.g. requirements.txt in python and pre-built containers)
3) Large files that cannot be stored in source code like weights files,
   data files, etc should be stored separately
4) Configurations and hyperparameters that define your experiments (e.g.
   data split, alpha, beta, etc)
5) Performance metrics that evaluate your model (e.g. validation
   accuracy)

This framework has helped us keep track of our own models and keep
consistency across our processes. We wanted to share this with the
community of like-minded people and teams and help develop an open
standard for keeping track of model versions.

Requirements
------------

-  `openssl <https://github.com/openssl/openssl/blob/master/INSTALL>`__
-  `git <https://git-scm.com/book/en/v2/Getting-Started-Installing-Git>`__
-  `docker <https://docs.docker.com/engine/installation/>`__

Installation
------------

::

    pip install datmo

Project Structure
-----------------

Datmo adds ``.datmo`` directory which keeps track of all of the various
entities into a repository to make it datmo-enabled.

Project Templates
-----------------

In the ``/templates`` folder we have templates for those who will be
starting their projects from scratch.

Each folder includes a set of files that are not required by datmo but
that augment your project and may be useful as you start new projects.

Project Examples
----------------

In the ``/examples`` folder we have a few scripts you can run to get a
feel for datmo. You can navigate to `Examples </examples/README.md>`__
to learn more about how you can run the examples and get started with
your own projects.

Here's a comparison of a typical logistic regression model with one
leveraging Datmo.

Example
-------
+------------------------------------------------+--------------------------------------------+
| **Script to train a logistic regression**      | **The same script with Datmo**             |
+------------------------------------------------+--------------------------------------------+
| .. code:: python                               | .. code:: python                           |
|                                                |                                            |
|   from sklearn import datasets                 |   from sklearn import datasets             |
|   from sklearn import linear_model as lm       |   from sklearn import linear_model as lm   |
|   from sklearn import model_selection as ms    |   from sklearn import model_selection as ms|
|   from sklearn import externals as ex          |   from sklearn import externals as ex      |
|                                                |   import datmo # extra line                |
|                                                |                                            |
|                                                |                                            |
+------------------------------------------------+--------------------------------------------+

In order to run the above code you can do the following.

1. Navigate to a directory with a project

   ::

       $ mkdir MY_PROJECT
       $ cd MY_PROJECT

2. Initialize a datmo project

   ::

       $ datmo init

3. Copy the datmo code above into a ``train.py`` file in your
   ``MY_PROJECT`` directory
4. Run the script like you normally would in python

   ::

       $ python train.py

5. Congrats! You just created your first snapshot :) Now run an ls
   command for snapshots to see your first snapshot.

   ::

       $ datmo snapshot ls

Sharing (Beta)
--------------

Although datmo is made to track your changes locally, you can share a
project with your friends by doing the following (this is shown only for
git, if you are using another git tracking tool, you can likely do
something similar). NOTE: If your files are too big or cannot be added
to SCM then this may not work for you.

::

    $ git add -f .datmo/*
    $ git commit -m "my_message"
    $ git push 
    $ git push origin +refs/datmo/*:refs/datmo/*

The above will allow you to share datmo results and entities with
yourself or others on other machines. NOTE: you will have to remove
.datmo/ from tracking to start using datmo on the other machine. To do
that you can use the commands below

::

    $ git rm -r --cached
    $ git add .
    $ git commit -m "removed .datmo from tracking"

.. |PyPI version| image:: https://badge.fury.io/py/datmo.svg
   :target: https://badge.fury.io/py/datmo
.. |Build Status| image:: https://travis-ci.org/datmo/datmo.svg?branch=master
   :target: https://travis-ci.org/datmo/datmo
.. |Build status| image:: https://ci.appveyor.com/api/projects/status/5302d8a23qr4ui4y/branch/master?svg=true
   :target: https://ci.appveyor.com/project/asampat3090/datmo/branch/master
.. |Coverage Status| image:: https://coveralls.io/repos/github/datmo/datmo/badge.svg?branch=master
   :target: https://coveralls.io/github/datmo/datmo?branch=master
.. |Documentation Status| image:: https://readthedocs.org/projects/datmo/badge/?version=latest
   :target: http://datmo.readthedocs.io/en/latest/?badge=latest
.. |Codacy Badge| image:: https://api.codacy.com/project/badge/Grade/853b3d01b4424ac9aa72f9d5fead83b3
   :target: https://www.codacy.com/app/datmo/datmo
