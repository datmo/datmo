Datmo Concepts
===================================

Environments
-------------

**Environments** contain the hardware and software necessary for running code. These involve everything from programming languages, language-level packages/libraries, operating systems, and GPU drivers. 


Tasks
---------

**Tasks** are loggable command line actions a user takes within a project. For example, the commands ``python train.py`` or ``python predict.py`` would both be examples of tasks.


Snapshots
-------------

For recording state, we have our own fundamental unit called a **Snapshot**. This enables the user to have a single point of reference for the model version, rather than having to worry about individually tracking each component. Snapshots contain five components, each of which is logged at the time of Snapshot creation simultaneously.

- *Source code* is managed with a git file driver inside of a hidden `.datmo` folder. This prevents collisions with the user’s existing remote repository source control working tree. Users do not have to make git commits for Snapshots to save work, the `snapshot create` functions handle this behind the scenes for the user. Saving source code states to a remote repository still requires using git as per usual.


- *Environment* (dependencies, packages, libraries, system env) are stored in Dockerfiles for containerized task running and reproducibility on other systems. Datmo also currently autogenerates a `requirements.txt` file based on the packages imported by Python scripts in the repository.


- *Files* (visualizations, model weights files, datasets) fall into two classes -- files whose size and filetype permit being stored in source control (git) and those that do not. For the latter, typically found amongst large datasets, data streamed directly from database calls, or large weights files, they should be stored separately using your team’s method of choice. However, to ensure Snapshots deliver on the promise of having everything needed to reproduce the model, we strongly recommend referencing these locations in the configuration component with a pointer/path to identify where they are available (ex: S3 URL, database query, etc).


- *Configurations* are properties which alter your experiments (such as variable hyperparameters). Configurations are user defined, which can include (but are not limited to) algorithm type, framework, hyperparameters, external file locations, database queries, and more.

- *Metrics* are the values that help you assess your model (e.g. validation accuracy, training time, loss function score). These can be passed in from a memory-level variable/object in the Python SDK, or manually as a file or value via the CLI for all other languages.


Runs
--------------

A *run* is comprised of *tasks* and *snapshots*. Each run contains the initial state (snapshot), followed by the action that was performed to it (task), as well as the final state of the repository (another snapshot).


Workspaces
------------

Workspaces are interactive programming environments/IDE's. Depending on which environment is chosen during setup, there are a handful of workspaces that are available out of the box including:
    - Jupyter Notebook via ``$ datmo notebook``
    - RStudio via ``$ datmo rstudio``
    - JupyterLab *(coming soon)*