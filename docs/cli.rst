.. _cli:

Command Line Utility
****************************

The command line utility for datmo is to be used in tandem with the SDK and will typically be your first
contact with the datmo system. If using Python, see :ref:`python_sdk`.

If you are working within a repository already, you will want to run the :code:`datmo init` within your
repository in order to create your datmo project.

From there, you can create snapshots or run tasks using either the SDK or the CLI. At any given point you
can find out more about all of your snapshots using the :code:`datmo snapshot ls` command and see the status
of any of your tasks with the :code:`datmo task ls` command.

Sessions are a way for you to group together tasks and snapshots, but are completely optional. For example,
if you want to run a set of hyperparameter experiments modifying some subset of hyperparameters you might want to
do them in a designated session. Then you might try another set of hyperparameter sweeps which you would like to
group into another session. By default, you will always be in the "default" session unless otherwise specified.

You can delve through more of the commands and each of their parameters below to learn more about each entity
and how you can create different versions of them. You can also look through the `Getting Started section <https://github.com/datmo/datmo#getting-started>`_
in the README.


.. argparse::
   :module: datmo.cli.parser
   :func: get_datmo_parser
   :prog: datmo