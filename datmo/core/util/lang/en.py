MESSAGES = {
    "info": {
        "cli.general.line":
            "==============================================================",
        "cli.project.init.create":
            "Initializing project {name} @ ({path}) ",
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
        "cli.task.run":
            "Running a new task",
        "cli.task.stop":
            "Stopping task: %s",
        "cli.task.stop.all":
            "Stopping all tasks",
        "cli.task.stop.success":
            "Stopped task: %s",
        "cli.task.stop.all.success":
            "Stopped all tasks",
        "cli.session.create":
            "Created session '%s'",
        "cli.session.select":
            "Selecting new session '%s'",
        "cli.session.delete":
            "Removed session '%s'"
    },
    "warn": {
        "cli.general.internet":
            "Internet connectivity doesn't exist",
        "cli.general.git":
            "git isn't setup. please install git",
        "controller.general.environment.failed":
            "Environment driver not initialized",
        "controller.project.cleanup.refs":
            "Project code refs do not exist",
        "controller.project.cleanup.files":
            "Project files do not exist"
    },
    "error": {
        "exception.validationfailed":
            "Validation failed: %s",
        "sdk.snapshot.create.task.args":
            "Error due to passing excluded args while creating snapshot from task: %s",
        "cli.general":
            "An exception occurred: %s",
        "cli.general.method.not_found":
            "Method %s.%s not found",
        "cli.project":
            "No project found in the current directory: %s",
        "cli.task.run":
            "Error while running the task: %s",
        "cli.task.run.already_running":
            "Already task running with id: %s",
        "cli.task.stop":
            "Error while stopping the task: %s",
        "cli.task.stop.all":
            "Error while stopping all tasks",
        "cli.snapshot.create.task.args":
            "Error due to passing excluded args while creating snapshot from task: %s",
        "util.misc_functions.get_filehash":
            "Filepath does not point to a valid file: %s",
        "util.misc_functions.mutually_exclusive":
            "Mutually exclusive arguments passed: %s",
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
            "Commit ref given does not match a git commit within the tree: %s",
        "controller.code.driver.git.create_ref.no_commit":
            "Commit ref given does not match a git commit within the tree: %s",
        "controller.code.create":
            "Required argument not present in input",
        "controller.code.delete":
            "Code with id %s does NOT exist",
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
        "controller.environment.driver.docker.stop_container":
            "Error stopping docker container: %s",
        "controller.environment.driver.docker.remove_container":
            "Error removing docker container: %s",
        "controller.environment.driver.docker.stop_remove_containers_by_term":
            "Error stopping and removing containers by term: %s",
        "controller.environment.create":
            "Required argument definition_filepath not present in input",
        "controller.environment.requirements.create":
            "Error while creating requirements file for python: %s",
        "controller.environment.build":
            "Environment with id %s does NOT exist",
        "controller.environment.delete":
            "Environment with id %s does NOT exist",
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
        "controller.base.__init__":
            "Project path does not exist: %s",
        "controller.base.current_session":
            "Model object does not exist within project",
        "controller.project.init.arg":
            "Required argument %s not present in input",
        "controller.project.init":
            "Session does not exist",
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
        "controller.session.delete.default":
            "Can not delete default session",
        "storage.local.dal.update":
            "Entity id not provided in the input for update",
    },
    "debug": {},
    "trace": {},
    "fatal": {},
    "prompt": {
        "cli.project.init.name":
            "Enter name for the project",
        "cli.project.init.description":
            "Enter description for the project",
        "cli.project.init.git":
            "Enter remote git url for the Datmo project",
        "cli.general.confirm":
            "Is it okay?",
        "cli.project.cleanup.confirm":
            "Are you sure you want to delete all datmo project information? [yN]",
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
        """
    }
}


def get_messages():
    return MESSAGES
