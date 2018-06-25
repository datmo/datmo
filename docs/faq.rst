Frequently asked Questions
===================================

Q: What is the role of the datmo open source tool?

A: The open source project acts as a user-controlled project manager (available as both a CLI and Python SDK) that enables users to create, run, manage, and record all aspects of their experiments.

-----

Q: Do I have to know how to use Docker to use Datmo?

A: Not at all!

------

Q: How can I add my own environments to be used with Datmo?

A: The ``environment setup`` command has the ability to import a file or set of files as a Datmo environment (ie: Dockerfile, requirements.txt, package.json, etc). You can then pass this environment ID at the time of task run. Datmo sets the most recent environment that was setup as the default for running tasks.

------

Q: How does Datmo handle all of my different environments?

A: The default environment that will be used for running tasks at any given time is chosen by the Dockerfile that is present in the ``datmo_environment`` directory. The other environments locally available for your project, visible with ``$ datmo environment ls``, can be selected by passing the environment ID in as a parameter at the time of a task run. 

-----

Q: I've made changes to the Dockerfile in my project, but the container environment isn't changing too. Why is this?

A: When running a task, Datmo always looks first inside the ``datmo_environment`` directory. If an environment is not present there, it will then use a Dockerfile from the project's root directory (if present). However, after the first run, Datmo creates an environment entity and Dockerfile that are replicas of the one used at the time of the initial run. Because of the priority of environment directories, Datmo will utilize the Dockerfile from the ``datmo_environment`` for subsequent runs, which means that changes to the original Dockerfile outside of ``datmo_environment`` will not appear in the Dockerfile/environment Datmo has created/tracked.