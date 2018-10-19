MESSAGES = {
    "info": {
        "cli.general.line":
            "==============================================================",
        "cli.project.init.create":
            "Initializing project @ ({path}) ",
        "cli.project.init.create.success":
            "Created project {name} @ ({path}) ",
        "cli.project.init.create.failure":
            "Failed to create project {name} @ ({path}) ",
        "cli.project.init.update":
            "Updating project {name} @ ({path}) ",
        "cli.project.init.update.success":
            "Updated project {name} @ ({path}) ",
        "cli.project.init.update.failure":
            "Failed to update project {name} @ ({path}) ",
        "cli.workspace.notebook":
            "Starting a notebook",
        "cli.workspace.run.notebook":
            "Automatically opens on the browser if it exists",
        "cli.workspace.jupyterlab":
            "Starting a jupyter lab",
        "cli.workspace.run.jupyterlab":
            "Automatically opens on the browser if it exists",
        "cli.workspace.terminal":
            "Starting a terminal",
        "cli.workspace.rstudio":
            "Starting a rstudio",
        "cli.workspace.run.rstudio":
            "Automatically opens http://localhost:8787 to login to rstudio,"
            "enter username: rstudio and password: rstudio",
        "cli.project.pull":
            "Pulling information from the Datmo project url and adding it to local...",
        "cli.project.update":
            "Update Datmo project",
        "cli.project.cleanup":
            "Cleaning up project {name} @ ({path}) ",
        "cli.project.cleanup.success":
            "Removed project {name} @ ({path}) ",
        "cli.project.cleanup.failure":
            "Failed to remove project {name} @ ({path}) ",
        "cli.general.abort":
            u'\u274c' + "  Your changes have been aborted!",
        "cli.general.success":
            u'\u2713' +
            " You have successfully re-initialized your local Datmo project here %s",
        "cli.general.project.create":
            "Creating a new Datmo project",
        "cli.general.str.test":
            "%s",
        "cli.general.dict.test":
            "{foo} - {bar}",
        "cli.general.tuple.test":
            "%s, %s",
        "cli.environment.setup.success":
            "Successful setup of an environment with name: %s and id: %s",
        "cli.environment.create":
            "Creating a new environment",
        "cli.environment.create.success":
            "Created a new environment with id: %s",
        "cli.environment.create.alreadyexist":
            "No changes in environment definition files from id: %s",
        "cli.environment.delete.success":
            "Deleted environment with id: %s",
        "cli.snapshot.create":
            "Creating a new snapshot",
        "cli.snapshot.create.success":
            "Created snapshot with id: %s",
        "cli.snapshot.delete":
            "Deleting a snapshot",
        "cli.snapshot.delete.success":
            "Deleted snapshot with id: %s",
        "cli.snapshot.update":
            "Updating a snapshot",
        "cli.snapshot.update.success":
            "Updated snapshot with id: %s",
        "cli.snapshot.checkout.success":
            "Moved to snapshot with id: %s",
        "cli.run.run":
            "Running a script",
        "cli.run.rerun":
            "Rerunning run with id: %s",
        "cli.deploy.service":
            "Deploying a service...",
        "cli.run.run.stop":
            "Stopping the run...",
        "cli.run.run.complete":
            "Completed run: %s",
        "cli.run.stop":
            "Stopping the run: %s",
        "cli.run.stop.all":
            "Stopping all runs",
        "cli.run.stop.success":
            "Stopped run: %s",
        "cli.run.stop.all.success":
            "Stopped all runs",
        "cli.run.delete":
            "Deleting a run: %s",
        "cli.run.delete.success":
            "Deleted run: %s",
        "cli.session.create":
            "Created session '%s'",
        "cli.session.select":
            "Selecting new session '%s'",
        "cli.session.update":
            "Updated session '%s'",
        "cli.session.delete":
            "Removed session '%s'",
        "cli.deploy.service.update_server":
            "Deployments can only have 1 server type, currently deployment %s is deployed with server type %s. "
            "If you want to change the server type, delete the deployment using `datmo deploy rm` and re-deploy",
        "cli.deploy.service.update_deploy":
            "Use the update command to re-deploy new code or to scale the size of your deployment",
        "cli.deploy.service.success":
            "Successfully deployed as %s",
        "cli.deploy.update.create_deployment":
            "Create deployment using the `datmo deploy` command",
        "cli.deploy.update.success":
            "Successfully deployed as %s",
        "cli.deploy.logs.download":
            "Downloading compressed io logs for service route %s for date %s...",
        "cli.deploy.rm.removing":
            "Removing all the services and servers in your deployment",
        "cli.deploy.rm.success":
            "Successfully removed deployment: %s"
    },
    "warn": {
        "cli.general.internet":
            "Internet connectivity doesn't exist",
        "cli.general.git":
            "git isn't setup. please install git",
        "controller.general.environment.failed":
            "Environment driver not initialized",
        "controller.project.cleanup.not_init":
            "No valid datmo project was detected",
        "controller.project.cleanup.environment":
            "Error cleaning up project environment",
        "controller.project.cleanup.code":
            "Error cleaning up project code",
        "controller.project.cleanup.files":
            "Error cleaning up project files",
        "cli.environment.setup.argument.unavailable.type":
            "This name or index does not match any supported environment types: %s, please re-enter the type",
        "cli.environment.setup.argument.unavailable.framework":
            "This name or index does not match any supported environment frameworks: %s, please re-enter the framework",
        "cli.environment.setup.argument.unavailable.language":
            "This name or index does not match any supported environment language: %s, please re-enter the option",
        "cli.environment.setup.argument.type":
            "No user input detected for environment type, defaulting to option: cpu",
        "cli.environment.setup.argument.framework":
            "No user input detected for environment framework, defaulting to option: python-base",
        "cli.environment.setup.argument.language":
            "No user input detected for environment language, defaulting to option: py27",
        "cli.deploy.service.deployment_exists":
            "Deployment already exists with server type: %s",
        "cli.deploy.update.deployment_exists":
            "Deployment already exists with server type: %s",
    },
    "error": {
        "exception.validationfailed":
            "Validation failed: %s",
        "general.project.dne":
            "datmo project structure not found in current directory. Run `datmo init` to initialize",
        "general.environment.docker.na":
            "Docker daemon is not initialized. This command cannot be run. Please start Docker and try again.",
        "sdk.snapshot.create.run.args":
            "Error due to passing excluded args while creating snapshot from run: %s",
        "cli.general":
            "An exception occurred: %s",
        "cli.general.method.not_found":
            "Method %s.%s not found",
        "cli.project":
            "No project found in the current directory: %s",
        "cli.workspace.notebook":
            "Error while running the notebook with id: %s",
        "cli.workspace.jupyterlab":
            "Error while running the jupyterlab with id: %s",
        "cli.workspace.terminal":
            "Error while running the terminal with id: %s",
        "cli.workspace.rstudio":
            "Error while running the rstudio with id: %s",
        "cli.session.update.dne":
            "No session found with given id: %s",
        "cli.session.delete.dne":
            "No session found with given name or id: %s",
        "cli.session.delete.default":
            "Cannot delete default session",
        "cli.session.select.dne":
            "No session found with given name or id: %s",
        "cli.run.run":
            "Error while running the script: %s",
        "cli.run.run.data.files.limit_exceeded":
            "Limit by passing only one file. Else, pass directories for data",
        "cli.run.run.data.src_dir.dne":
            "Data directory being passed doesn't exist: %s",
        "cli.run.run.data.src_file.dne":
            "Data file being passed doesn't exist: %s",
        "cli.run.run.already_running":
            "Already running with id: %s",
        "cli.run.stop":
            "Error while stopping the run: %s",
        "cli.run.parse.paths":
            "Error with Data: %s",
        "cli.run.stop.all":
            "Error while stopping all runs",
        "cli.run.delete":
            "Error while deleting the run: %s",
        "cli.snapshot.create.run.args":
            "Error due to passing excluded args while creating snapshot from run: %s",
        "cli.snapshot.checkout.failure":
            "Error while checking out to a snapshot due to unstaged changes",
        "cli.deploy.subcommand":
            "Error in usage of the command. Select amongst setup, service, update, ls, rm, logs for deploy command",
        "cli.deploy.update.deployment_dne":
            "No deployment exists with this name %s",
        "cli.deploy.logs.download_error":
            "error: while extracting logs. error due to following,\n %s",
        "util.misc_functions.get_filehash":
            "Filepath does not point to a valid file: %s",
        "util.misc_functions.mutually_exclusive":
            "Mutually exclusive arguments passed: %s",
        "controller.code.driver.file.create_ref.no_commit":
            "Commit ref given does not match an existing commit: %s",
        "controller.code.driver.file.create_ref.cannot_commit":
            "Commit failed, no files to commit",
        "controller.code.driver.file.delete_ref":
            "Commit ref does not exist",
        "controller.code.driver.file.checkout_ref":
            "Commit ref does not exist",
        "controller.code.driver.git.__init__.dne":
            "File path does not exist: %s",
        "controller.code.driver.git.__init__.giterror":
            "Error in git: %s",
        "controller.code.driver.git.__init__.gitversion":
            "Git version must be later than 1.9.7. Current version: %s",
        "controller.code.driver.git.__init__.datmo":
            "Datmo folder exists in work tree. Remove and retry",
        "controller.code.driver.git.init":
            "Error in git: %s",
        "controller.code.driver.git.init.file":
            "Error inadding datmo refs and files: %s",
        "controller.code.driver.git._parse_git_url.url":
            "Url not valid: %s",
        "controller.code.driver.git._parse_git_url.access":
            "Remote access not configured for https or ssh: %s",
        "controller.code.driver.git.clone":
            "Error in git clone with url %s: %s",
        "controller.code.driver.git.add":
            "Error in git add for filepath %s: %s",
        "controller.code.driver.git.commit":
            "Error in git commit with options %s: %s",
        "controller.code.driver.git.branch":
            "Error in git branch with name %s: %s",
        "controller.code.driver.git.status":
            "Error in git status",
        "controller.code.driver.git.checkout":
            "Error in git checkout with name %s: %s",
        "controller.code.driver.git.stash_save":
            "Error in git stash save: %s",
        "controller.code.driver.git.stash_list":
            "Error in git stash list: %s",
        "controller.code.driver.git.stash_pop":
            "Error in git stash pop: %s",
        "controller.code.driver.git.stash_apply":
            "Error in git stash_apply: %s",
        "controller.code.driver.git.latest_commit":
            "Error in git latest commit: %s",
        "controller.code.driver.git.reset":
            "Error in git reset: %s",
        "controller.code.driver.git.check_git_work_tree":
            "Error in git check work tree: %s",
        "controller.code.driver.git.remote":
            "Error in git remote -- mode: %s, origin: %s, git_url: %s -- %s",
        "controller.code.driver.git.get_remote_url":
            "Error in git get remote url: %s",
        "controller.code.driver.git.fetch":
            "Error in git fetch -- origin: %s, name: %s -- %s",
        "controller.code.driver.git.push":
            "Error in git push -- origin: %s -- %s",
        "controller.code.driver.git.ensure_gitignore_exists":
            "Error in ensuring gitignore: %s",
        "controller.code.driver.git.ensure_code_refs_dir":
            "Error in ensuring datmo code refs dir: %s",
        "controller.code.driver.git.delete_code_refs_dir":
            "Error in deleting datmo code refs dir: %s",
        "controller.code.driver.git.delete_ref":
            "Commit ref does not exist",
        "controller.code.driver.git.push_ref":
            "Error in git push code ref: %s",
        "controller.code.driver.git.fetch_ref":
            "Error in git fetch code ref with id %s: %s",
        "controller.code.driver.git.checkout_ref":
            "Error in git checkout code ref with id %s: %s",
        "controller.code.driver.git.create_ref.cannot_commit":
            "Git commit failed: %s",
        "controller.code.driver.git.create_ref.no_commit":
            "Commit ref given does not match a git commit within the tree: %s",
        "controller.code.create":
            "Required argument not present in input",
        "controller.code.delete":
            "Code with id %s does NOT exist",
        "controller.code.checkout":
            "Code id does not exist: %s",
        "controller.environment.__init__":
            "Project has not been initialized ",
        "controller.environment.driver.docker.__init__.dne":
            "File path does not exist: %s",
        "controller.environment.driver.docker.__init__":
            "Docker environment management initialization failed. Platform: %s",
        "controller.environment.driver.docker.init":
            "Error in docker initialization: %s",
        "controller.environment.driver.docker.get_tags":
            "Error in getting tags: %s",
        "controller.environment.driver.docker.create.dne":
            "path does not exist: %s",
        "controller.environment.driver.docker.setup.dne":
            "input environment does not exist: %s, Update Dockerfile with image name in environment folder",
        "controller.environment.driver.docker.create.exists":
            "output path already exists: %s",
        "controller.environment.driver.docker.build_image":
            "Error in docker build: %s",
        "controller.environment.driver.docker.remove_image":
            "Error in docker rmi: %s",
        "controller.environment.driver.docker.remove_images":
            "Error in running multiple rmi commands: %s",
        "controller.environment.driver.docker.run_container":
            "Error running docker container. Failed command: %s",
        "controller.environment.driver.docker.exec_container":
            "Error executing inside docker container. Failed command: %s",
        "controller.environment.driver.docker.stop_container":
            "Error stopping docker container: %s",
        "controller.environment.driver.docker.remove_container":
            "Error removing docker container: %s",
        "controller.environment.driver.docker.stop_remove_containers_by_term":
            "Error stopping and removing containers by term: %s",
        "controller.environment.setup.unstaged":
            "Unstaged changes found in project environment directory: %s",
        "controller.environment.create":
            "Required argument paths not present in input",
        "controller.environment.create.filepath.dne":
            "Path specified in definition paths does not exist: %s",
        "controller.environment.checkout":
            "Environment id does not exist: %s",
        "controller.environment.requirements.create":
            "Error while creating requirements file for python: %s",
        "controller.environment.build":
            "Environment with id %s does NOT exist",
        "controller.environment.delete":
            "Environment with id %s does NOT exist",
        "controller.file.driver.create_collection.file_exists":
            "File name has already been specified and exists: %s",
        "controller.file.driver.create_collection.dir_exists":
            "Dir name has already been specified and exists: %s",
        "controller.file.driver.local.__init__":
            "File path does not exist: %s",
        "controller.file.driver.local.get_safe_dst_filepath.src":
            "Source filepath is not a valid file: %s",
        "controller.file.driver.local.get_safe_dst_filepath.dst":
            "Destination directory path is not a valid directory: %s",
        "controller.file.driver.local.copytree.src":
            "Source directory path is not a valid directory: %s",
        "controller.file.driver.local.copytree.dst":
            "Destination directory path is not a valid directory: %s",
        "controller.file.driver.local.copyfile.src":
            "Source filepath is not a valid file: %s",
        "controller.file.driver.local.copyfile.dst":
            "Destination directory path is not a valid directory: %s",
        "controller.file.driver.local.init":
            "Failed to ensure datmo file structure: %s",
        "controller.file.driver.local.get":
            "Path specified does not exist: %s",
        "controller.file.driver.local.delete":
            "Path specified does not exist: %s",
        "controller.file.driver.local.create_collections_dir":
            "Project file structure is not properly initialized",
        "controller.file.driver.local.create_collection.structure":
            "Project file structure is not properly initialized",
        "controller.file.driver.local.create_collection.filepath":
            "Filepath %s given does not exist; aborting create collection",
        "controller.file.driver.local.transfer_collection":
            "Collection with id %s does not currently exist",
        "controller.file.driver.local.transfer_collection.dst":
            "Destination directory path is not a valid directory: %s",
        "controller.file.driver.local.list_file_collections":
            "Project file structure is not properly initialized",
        "controller.file_collection.create":
            "Required argument not present in input",
        "controller.file_collection.delete":
            "FileCollection with id %s does NOT exist",
        "controller.file_collection.checkout_file":
            "FileCollection id does NOT exist",
        "controller.base.__init__":
            "Project path does not exist: %s",
        "controller.base.current_session":
            "Model object does not exist within project",
        "controller.project.init.arg":
            "Required argument %s not present in input",
        "controller.project.status":
            "Project has not been initialized",
        "controller.snapshot.__init__":
            "Project has not been initialized",
        "controller.snapshot.create.arg":
            "Required argument missing to create snapshot: %s",
        "controller.snapshot.create.file_config":
            "Config file does not exist",
        "controller.snapshot.create.file_stat":
            "Stats file does not exist",
        "controller.snapshot.create_from_task":
            "Task specified by id %s has not been completed",
        "controller.snapshot.list":
            "Session does not exist for id: %s",
        "controller.snapshot.delete.arg":
            "Delete argument %s not present in input",
        "controller.task.__init__":
            "Project has not been initialized",
        "controller.task._run_helper.env_dne":
            "Environment specified does not exist: %s",
        "controller.task.run.arg":
            "Required argument is missing to run task: %s",
        "controller.task.run":
            "Error creating task directory for run: %s",
        "controller.task.run.args.detach.interactive":
            "Error in running tasks since both detach and interactive is used",
        "controller.task.stop.arg":
            "Stop argument %s not present in input",
        "controller.task.stop.arg.missing":
            "Stop argument %s unable to stop environment. please use -a to stop all running tasks",
        "controller.task.list":
            "Session does not exist for id: %s",
        "controller.task.delete.arg":
            "Delete argument %s not present in input",
        "controller.session.__init__":
            "Project has not been initialized",
        "controller.session.update.default":
            "Cannot update default session",
        "controller.session.delete.default":
            "Cannot delete default session",
        "storage.local.dal.update":
            "Entity id not provided in the input for update",
    },
    "debug": {},
    "trace": {},
    "fatal": {},
    "prompt": {
        "cli.environment.setup.framework":
            "Please select one of the above environments (e.g. 1 or data-analytics)",
        "cli.environment.setup.type":
            "Please select one of the above environment type (e.g. 1 or gpu)",
        "cli.environment.setup.language":
            "Please select one of the above environment language (e.g. py27)",
        "cli.project.init.name":
            "Enter name for the project",
        "cli.project.init.description":
            "Enter description for the project",
        "cli.project.init.git":
            "Enter remote git url for the Datmo project",
        "cli.general.confirm":
            "Is it okay?",
        "cli.project.cleanup.confirm":
            "Are you sure you want to delete all datmo project information along with files and environment directory? "
            "If none found, no changes will be made [yN]",
        "cli.project.environment.setup":
            "Would you like to setup the environment? [yN]",
        "cli.project.deploy.service.name":
            "Enter name for your deployment",
        "cli.project.deploy.update.name":
            "Enter name for the deployment you want to update (use `datmo deploy ls` to see a list)",
        "cli.project.deploy.service.server_type":
            "Enter the type of AWS EC2 server to be used for your deployment (e.g. t2.small, etc)",
        "cli.project.deploy.service.size":
            "Enter the number of AWS EC2 servers for your deployment (e.g. 1, 2, etc)",
        "cli.project.deploy.update.size":
            "Enter the updated number of AWS EC2 servers for your deployment (e.g. 1, 2, etc)",
        "cli.project.deploy.logs.service_path":
            "Enter the service path to get the logs for the deployed datmo service",
        "cli.project.deploy.rm.service_name":
            "Enter name for the deployment to be removed"
    },
    "argparser": {
        "cli.datmo.usage":
            """
Datmo is a command line utility to enable tracking of data science projects.
It uses many of the tools you are already familiar with and combines them into a snapshot
which allows you to keep track of 5 components at once

1) Source Code
2) Dependency Environment
3) Large Files
4) Configurations
5) Metrics
        """,
        "cli.snapshot.usage":
            """""",
        "cli.snapshot.description":
            """ 
Datmo snapshots allow you to save the state of your model and experiments
by keeping track of your source code, environment, configuration, metrics
and large files.
            """,
        "cli.snapshot.create.description":
            """
Run snapshot create any time you want to save the results of your 
experiments. You can then view all snapshots with the `snapshot ls` command.
        """,
        "cli.deploy.description":
            """
Datmo deploy allows you to deploy a version of your model by using the 
datmo_deploy.yml and running `datmo deploy service`
            """
    }
}


def get_messages():
    return MESSAGES
