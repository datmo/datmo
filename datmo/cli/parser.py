from datmo.cli.driver.parser import Parser

parser = Parser(
prog="datmo",
usage=
"""
datmo COMMAND [SUBCOMMANDS] ARGS 

Datmo is a command line utility to enable tracking of data science projects. 
It uses many of the tools you are already familiar with and combines them into a snapshot
which allows you to keep track of 5 components at once

1) Source Code
2) Dependency Environment
3) Large Files
4) Configurations
5) Metrics

command: 
""")

subparsers = parser.add_subparsers(
    title="commands", dest="command")

# Project
init_parser = subparsers.add_parser(
            "init", help="Initialize project")
init_parser.add_argument("--name", default=None)
init_parser.add_argument("--description", default=None)

# Session
session_parser = subparsers.add_parser(
            "session", help="Session module")
session_subcommand_parsers = session_parser.add_subparsers(
    title="subcommands", dest="subcommand")

session_create = session_subcommand_parsers.add_parser("create", help="Create session")
session_create.add_argument(
    "--name", "-m", dest="name", default="", help="Session name")
session_create.add_argument(
    "--current",
    dest="current",
    action="store_false",
    help="Boolean if you want to switch to this session")

session_delete = session_subcommand_parsers.add_parser(
    "delete", help="Delete a snapshot by id")
session_delete.add_argument(
    "--name", dest="name", help="Name of session to delete")

session_ls = session_subcommand_parsers.add_parser("ls", help="List sessions")

session_select = session_subcommand_parsers.add_parser(
    "select", help="Select a session")
session_select.add_argument(
    "--name", dest="name", help="Name of session to select")

# Snapshot
snapshot_parser = subparsers.add_parser(
            "snapshot", help="Snapshot module")
snapshot_subcommand_parsers = snapshot_parser.add_subparsers(
    title="subcommands", dest="subcommand")

snapshot_create = snapshot_subcommand_parsers.add_parser(
    "create", help="create snapshot")
snapshot_create.add_argument(
    "--message",
    "-m",
    dest="message",
    default=None,
    help="message to describe snapshot")
snapshot_create.add_argument(
    "--label",
    "-l",
    dest="label",
    default=None,
    help="Label snapshots with a category (e.g. best)")
snapshot_create.add_argument(
    "--session-id",
    dest="session_id",
    default=None,
    help="user given session id")

snapshot_create.add_argument(
    "--task-id",
    dest="task_id",
    default=None,
    help="Specify task id to pull information from")

snapshot_create.add_argument(
    "--code-id",
    dest="code_id",
    default=None,
    help="code id from code object")
snapshot_create.add_argument(
    "--commit-id",
    dest="commit_id",
    default=None,
    help="commit id from source control")

snapshot_create.add_argument(
    "--environment-id",
    dest="environment_id",
    default=None,
    help="environment id from environment object")
snapshot_create.add_argument(
    "--environment-def-path",
    dest="environment_def_path",
    default=None,
    help=
    "absolute filepath to environment definition file (e.g. /path/to/Dockerfile)"
)

snapshot_create.add_argument(
    "--file-collection-id",
    dest="file_collection_id",
    default=None,
    help="file collection id for file collection object")
snapshot_create.add_argument(
    "--filepaths",
    dest="filepaths",
    default=None,
    action="append",
    help=
    "absolute paths to files or folders to include within the files of the snapshot"
)

snapshot_create.add_argument(
    "--config-filename",
    dest="config_filename",
    default=None,
    help="filename to use to search for configuration JSON")
snapshot_create.add_argument(
    "--config-filepath",
    dest="config_filepath",
    default=None,
    help="absolute filepath to use to search for configuration JSON")

snapshot_create.add_argument(
    "--stats-filename",
    dest="stats_filename",
    default=None,
    help="filename to use to search for metrics JSON")
snapshot_create.add_argument(
    "--stats-filepath",
    dest="stats_filepath",
    default=None,
    help="absolute filepath to use to search for metrics JSON")

snapshot_delete = snapshot_subcommand_parsers.add_parser(
    "delete", help="Delete a snapshot by id")
snapshot_delete.add_argument("--id", dest="id", help="snapshot id to delete")

snapshot_ls = snapshot_subcommand_parsers.add_parser("ls", help="List snapshots")
snapshot_ls.add_argument(
    "--session-id",
    dest="session_id",
    default=None,
    help="Session ID to filter")
snapshot_ls.add_argument(
    "--all",
    "-a",
    dest="details",
    action="store_true",
    help="Show detailed snapshot information")

snapshot_checkout = snapshot_subcommand_parsers.add_parser(
    "checkout", help="Checkout a snapshot by id")
snapshot_checkout.add_argument(
    "--id", dest="id", default=None, help="Snapshot ID")

# Task
task_parser = subparsers.add_parser("task", help="Task module")
task_subcommand_parsers = task_parser.add_subparsers(
    title="subcommands", dest="subcommand")

# Task run arguments
task_run = task_subcommand_parsers.add_parser("run", help="Run task")
task_run.add_argument(
    "--gpu",
    dest="gpu",
    action="store_true",
    help="Boolean if you want to run using GPUs")
task_run.add_argument(
    "--ports",
    dest="ports",
    default=None,
    action="append",
    type=str,
    help="""
    Network port mapping during task (e.g. 8888:8888). Left is the host machine port and right
    is the environment port available during a run.
""")
# run.add_argument("--data", nargs="*", dest="data", type=str, help="Path for data to be used during the Task")
task_run.add_argument(
    "--env-def",
    dest="environment_definition_filepath",
    default=None,
    type=str,
    help=
    "Pass in the Dockerfile with which you want to build the environment"
)
task_run.add_argument(
    "--interactive",
    dest="interactive",
    action="store_true",
    help="Run the environment in interactive mode (keeps STDIN open)")
task_run.add_argument("cmd", nargs="?", default=None)

# Task list arguments
task_ls = task_subcommand_parsers.add_parser("ls", help="List tasks")
task_ls.add_argument(
    "--session-id",
    dest="session_id",
    default=None,
    nargs="?",
    type=str,
    help="Pass in the session id to list the tasks in that session")

# Task stop arguments
task_stop = task_subcommand_parsers.add_parser("stop", help="Stop tasks")
task_stop.add_argument(
    "--id", dest="id", default=None, type=str, help="Task ID to stop")