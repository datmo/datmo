from datmo.core.util.i18n import get as __
from datmo.cli.driver.parser import Parser


def get_datmo_parser():
    parser = Parser(prog="datmo")

    subparsers = parser.add_subparsers(title="commands", dest="command")

    # Project
    init_parser = subparsers.add_parser("init", help="initialize project")
    init_parser.add_argument("--name", default=None)
    init_parser.add_argument("--description", default=None)

    version_parser = subparsers.add_parser("version", help="datmo version")

    status_parser = subparsers.add_parser("status", help="project status")

    cleanup_parser = subparsers.add_parser("cleanup", help="remove project")

    # Session
    session_parser = subparsers.add_parser("session", help="session module")
    session_subcommand_parsers = session_parser.add_subparsers(
        title="subcommands", dest="subcommand")

    session_create = session_subcommand_parsers.add_parser(
        "create", help="create session")
    session_create.add_argument(
        "--name", "-m", dest="name", default="", help="session name")
    session_create.add_argument(
        "--current",
        dest="current",
        action="store_false",
        help="boolean if you want to switch to this session")

    session_delete = session_subcommand_parsers.add_parser(
        "delete", help="delete a session by id")
    session_delete.add_argument(
        "--name", dest="name", help="name of session to delete")

    session_ls = session_subcommand_parsers.add_parser(
        "ls", help="list sessions")

    session_select = session_subcommand_parsers.add_parser(
        "select", help="select a session")
    session_select.add_argument(
        "--name", dest="name", help="name of session to select")

    # Snapshot
    snapshot_parser = subparsers.add_parser(
        "snapshot", description=__("argparser", "cli.snapshot.description"))
    snapshot_subcommand_parsers = snapshot_parser.add_subparsers(
        title="subcommands", dest="subcommand")

    snapshot_create = snapshot_subcommand_parsers.add_parser(
        "create",
        description=__("argparser", "cli.snapshot.create.description"))
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
        help="label snapshots with a category (e.g. best)")
    snapshot_create.add_argument(
        "--session-id",
        dest="session_id",
        default=None,
        help="user given session id")

    snapshot_create.add_argument(
        "--task-id",
        dest="task_id",
        default=None,
        help="specify task id to pull information from")

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
        "--environment-def",
        dest="environment_definition_filepath",
        default=None,
        type=str,
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
        "--config",
        "-c",
        dest="config",
        default=None,
        action="append",
        type=str,
        help="""
            provide key, value pair for the config such as key:value, (e.g. accuracy:91.1). Left is the key and 
            right is the value for it.
        """)

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
    snapshot_create.add_argument(
        "--stats",
        "-s",
        dest="stats",
        default=None,
        action="append",
        type=str,
        help="""
                provide key, value pair for the stats such as key:value, (e.g. accuracy:91.1). Left is the key and 
                right is the value for it.
        """)

    snapshot_update = snapshot_subcommand_parsers.add_parser(
        "update", help="update a snapshot by id")
    snapshot_update.add_argument(
        "--id", dest="id", help="snapshot id to update")
    snapshot_update.add_argument(
        "--config",
        "-c",
        dest="config",
        default=None,
        action="append",
        type=str,
        help="""
        provide key, value pair for the config such as key:value, (e.g. accuracy:91.1). Left is the key and 
        right is the value for it.
    """)
    snapshot_update.add_argument(
        "--stats",
        "-s",
        dest="stats",
        default=None,
        action="append",
        type=str,
        help="""
        provide key, value pair for the stats such as key:value, (e.g. accuracy:91.1). Left is the key and 
        right is the value for it.
    """)
    snapshot_update.add_argument(
        "--message", dest="message", help="new message for the snapshot")
    snapshot_update.add_argument(
        "--label", dest="label", help="new label for the snapshot")

    snapshot_delete = snapshot_subcommand_parsers.add_parser(
        "delete", help="delete a snapshot by id")
    snapshot_delete.add_argument(
        "--id", dest="id", help="snapshot id to delete")

    snapshot_ls = snapshot_subcommand_parsers.add_parser(
        "ls", help="list snapshots")
    snapshot_ls.add_argument(
        "--session-id",
        dest="session_id",
        default=None,
        help="session id to filter")
    snapshot_ls.add_argument(
        "--all",
        "-a",
        dest="details",
        action="store_true",
        help="show detailed snapshot information")

    snapshot_checkout = snapshot_subcommand_parsers.add_parser(
        "checkout", help="checkout a snapshot by id")
    snapshot_checkout.add_argument("id", default=None, help="snapshot id")

    snapshot_diff = snapshot_subcommand_parsers.add_parser(
        "diff", help="view diff between 2 snapshots")
    snapshot_diff.add_argument("id_1", default=None, help="snapshot id 1")
    snapshot_diff.add_argument("id_2", default=None, help="snapshot id 2")

    snapshot_inspect = snapshot_subcommand_parsers.add_parser(
        "inspect", help="inspect a snapshot by id")
    snapshot_inspect.add_argument("id", default=None, help="snapshot id")

    # Task
    task_parser = subparsers.add_parser("task", help="task module")
    task_subcommand_parsers = task_parser.add_subparsers(
        title="subcommands", dest="subcommand")

    # Task run arguments
    task_run = task_subcommand_parsers.add_parser("run", help="run task")
    task_run.add_argument(
        "--gpu",
        dest="gpu",
        action="store_true",
        help="boolean if you want to run using GPUs")
    task_run.add_argument(
        "--ports",
        "-p",
        dest="ports",
        default=None,
        action="append",
        type=str,
        help="""
        network port mapping during task (e.g. 8888:8888). Left is the host machine port and right
        is the environment port available during a run.
    """)
    # run.add_argument("--data", nargs="*", dest="data", type=str, help="Path for data to be used during the Task")
    task_run.add_argument(
        "--environment-def",
        dest="environment_definition_filepath",
        default=None,
        type=str,
        help=
        "absolute filepath to environment definition file (e.g. /path/to/Dockerfile)"
    )
    task_run.add_argument(
        "--interactive",
        dest="interactive",
        action="store_true",
        help="run the environment in interactive mode (keeps STDIN open)")
    task_run.add_argument(
        "cmd",
        nargs="?",
        default=None,
        help="command to run within environment")

    # Task list arguments
    task_ls = task_subcommand_parsers.add_parser("ls", help="list tasks")
    task_ls.add_argument(
        "--session-id",
        dest="session_id",
        default=None,
        nargs="?",
        type=str,
        help="pass in the session id to list the tasks in that session")

    # Task stop arguments
    task_stop = task_subcommand_parsers.add_parser("stop", help="stop tasks")
    task_stop.add_argument(
        "--id", dest="id", default=None, type=str, help="task id to stop")
    task_stop.add_argument(
        "--all",
        "-a",
        dest="all",
        action="store_true",
        help="stop all datmo tasks")

    return parser
