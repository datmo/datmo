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

    # Notebook
    notebook_parser = subparsers.add_parser(
        "notebook", help="To run jupyter notebook")
    notebook_parser.add_argument(
        "--gpu",
        dest="gpu",
        action="store_true",
        help="boolean if you want to run using GPUs")
    notebook_parser.add_argument(
        "--environment-id",
        dest="environment_id",
        default=None,
        help="environment id from environment object")
    notebook_parser.add_argument(
        "--environment-paths",
        dest="environment_paths",
        default=None,
        action="append",
        type=str,
        help=
        "list of absolute or relative filepaths and/or dirpaths to collect; can specify destination names with '>' (e.g. /path/to/file>hello, /path/to/file2, /path/to/dir>newdir)"
    )
    notebook_parser.add_argument(
        "--mem-limit",
        "-m",
        dest="mem_limit",
        default=None,
        type=str,
        help=
        "maximum amount of memory the notebook environment can use (these options take a positive integer, followed by a suffix of b, k, m, g, to indicate bytes, kilobytes, megabytes, or gigabytes)"
    )
    notebook_parser.add_argument(
        "--data",
        dest="data",
        default=None,
        action="append",
        type=str,
        help=
        "list of absolute or relative filepath and/or dirpaths for data; can specify destination names"
        " with '>' (e.g. /path/to/dir, /path/to/dir>newdir, /path/to/file)"
    )

    # Jupyterlab
    jupyterlab_parser = subparsers.add_parser(
        "jupyterlab", help="To run jupyterlab")
    jupyterlab_parser.add_argument(
        "--gpu",
        dest="gpu",
        action="store_true",
        help="boolean if you want to run using GPUs")
    jupyterlab_parser.add_argument(
        "--environment-id",
        dest="environment_id",
        default=None,
        help="environment id from environment object")
    jupyterlab_parser.add_argument(
        "--environment-paths",
        dest="environment_paths",
        default=None,
        action="append",
        type=str,
        help=
        "list of absolute or relative filepaths and/or dirpaths to collect; can specify destination names with '>' (e.g. /path/to/file>hello, /path/to/file2, /path/to/dir>newdir)"
    )
    jupyterlab_parser.add_argument(
        "--mem-limit",
        "-m",
        dest="mem_limit",
        default=None,
        type=str,
        help=
        "maximum amount of memory the jupyterlab environment can use (these options take a positive integer, followed by a suffix of b, k, m, g, to indicate bytes, kilobytes, megabytes, or gigabytes)"
    )
    jupyterlab_parser.add_argument(
        "--data",
        dest="data",
        default=None,
        action="append",
        type=str,
        help=
        "list of absolute or relative filepath and/or dirpaths for data; can specify destination names"
        " with '>' (e.g. /path/to/dir, /path/to/dir>newdir, /path/to/file)"
    )

    # Terminal
    terminal_parser = subparsers.add_parser("terminal", help="To run terminal")
    terminal_parser.add_argument(
        "--gpu",
        dest="gpu",
        action="store_true",
        help="boolean if you want to run using GPUs")
    terminal_parser.add_argument(
        "--environment-id",
        dest="environment_id",
        default=None,
        help="environment id from environment object")
    terminal_parser.add_argument(
        "--environment-paths",
        dest="environment_paths",
        default=None,
        action="append",
        type=str,
        help=
        "list of absolute or relative filepaths and/or dirpaths to collect; can specify destination names with '>' (e.g. /path/to/file>hello, /path/to/file2, /path/to/dir>newdir)"
    )
    terminal_parser.add_argument(
        "--mem-limit",
        "-m",
        dest="mem_limit",
        default=None,
        type=str,
        help=
        "maximum amount of memory the terminal environment can use (these options take a positive integer, followed by a suffix of b, k, m, g, to indicate bytes, kilobytes, megabytes, or gigabytes)"
    )
    terminal_parser.add_argument(
        "--data",
        dest="data",
        default=None,
        action="append",
        type=str,
        help=
        "list of absolute or relative filepath and/or dirpaths for data; can specify destination names"
        " with '>' (e.g. /path/to/dir, /path/to/dir>newdir, /path/to/file)"
    )

    # Rstudio
    rstudio_parser = subparsers.add_parser(
        "rstudio", help="To run Rstudio workspace")
    rstudio_parser.add_argument(
        "--environment-id",
        dest="environment_id",
        default=None,
        help="environment id from environment object")
    rstudio_parser.add_argument(
        "--environment-paths",
        dest="environment_paths",
        default=None,
        action="append",
        type=str,
        help=
        "list of absolute or relative filepaths and/or dirpaths to collect; can specify destination names with '>' (e.g. /path/to/file>hello, /path/to/file2, /path/to/dir>newdir)"
    )
    rstudio_parser.add_argument(
        "--mem-limit",
        "-m",
        dest="mem_limit",
        default=None,
        type=str,
        help=
        "maximum amount of memory the rstudio environment can use (these options take a positive integer, followed by a suffix of b, k, m, g, to indicate bytes, kilobytes, megabytes, or gigabytes)"
    )
    rstudio_parser.add_argument(
        "--data",
        dest="data",
        default=None,
        action="append",
        type=str,
        help=
        "list of absolute or relative filepath and/or dirpaths for data; can specify destination names"
        " with '>' (e.g. /path/to/dir, /path/to/dir>newdir, /path/to/file)"
    )

    # Run
    run_parser = subparsers.add_parser("run", help="run module")

    # run arguments
    run_parser.add_argument(
        "--gpu",
        dest="gpu",
        action="store_true",
        help="boolean if you want to run using GPUs")
    run_parser.add_argument(
        "--ports",
        "-p",
        dest="ports",
        default=None,
        action="append",
        type=str,
        help="""
            network port mapping during run (e.g. 8888:8888). Left is the host machine port and right
            is the environment port available during a run.
        """)
    run_parser.add_argument(
        "--environment-id",
        dest="environment_id",
        default=None,
        help="environment id from environment object")
    run_parser.add_argument(
        "--environment-paths",
        dest="environment_paths",
        default=None,
        action="append",
        type=str,
        help=
        "list of absolute or relative filepaths and/or dirpaths to collect; can specify destination names with '>' (e.g. /path/to/file>hello, /path/to/file2, /path/to/dir>newdir)"
    )
    run_parser.add_argument(
        "--mem-limit",
        "-m",
        dest="mem_limit",
        default=None,
        type=str,
        help=
        "maximum amount of memory the task environment can use (these options take a positive integer, followed by a suffix of b, k, m, g, to indicate bytes, kilobytes, megabytes, or gigabytes. e.g. 4g)"
    )
    run_parser.add_argument(
        "--interactive",
        dest="interactive",
        action="store_true",
        help="run the environment in interactive mode (keeps STDIN open)")
    run_parser.add_argument(
        "cmd",
        nargs="?",
        default=None,
        help="command to run within environment")
    run_parser.add_argument(
        "--data",
        dest="data",
        default=None,
        action="append",
        type=str,
        help=
        "list of absolute or relative filepath and/or dirpaths for data; can specify destination names"
        " with '>' (e.g. /path/to/dir, /path/to/dir>newdir, /path/to/file)"
    )

    # List runs
    ls_runs_parser = subparsers.add_parser(
        "ls", help="To list all experiment runs")
    ls_runs_parser.add_argument(
        "--session-id",
        dest="session_id",
        default=None,
        nargs="?",
        type=str,
        help="pass in the session id to list the tasks in that session")
    ls_runs_parser.add_argument(
        "--format",
        dest="format",
        default="table",
        help="output format ['table', 'csv']")
    ls_runs_parser.add_argument(
        "--download",
        dest="download",
        action="store_true",
        help=
        "boolean is true if user would like to download. use --download-path to specify a path"
    )
    ls_runs_parser.add_argument(
        "--download-path",
        dest="download_path",
        default=None,
        help=
        "checked only if download is specified. saves output to location specified"
    )

    # Stop runs
    stop_run_parser = subparsers.add_parser("stop", help="stop runs")
    stop_run_parser.add_argument(
        "--id", dest="id", default=None, type=str, help="run id to stop")
    stop_run_parser.add_argument(
        "--all",
        "-a",
        dest="all",
        action="store_true",
        help="stop all datmo runs")

    # Delete runs
    delete_run_parser = subparsers.add_parser("delete", help="delete runs")
    delete_run_parser.add_argument("id", default=None, help="run id to delete")

    # Rerun
    rerun_parser = subparsers.add_parser(
        "rerun", help="To rerun an experiment")
    rerun_parser.add_argument("id", help="run id to be rerun")

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

    session_update = session_subcommand_parsers.add_parser(
        "update", help="update a session")
    session_update.add_argument("id", help="id of session to update")
    session_update.add_argument(
        "--name",
        dest="name",
        default=None,
        help="updated name of the session")

    session_delete = session_subcommand_parsers.add_parser(
        "delete", help="delete a session by name or id")
    session_delete.add_argument(
        "name_or_id", help="name or id of session to delete")

    session_ls = session_subcommand_parsers.add_parser(
        "ls", help="list sessions")
    session_ls.add_argument(
        "--format",
        dest="format",
        default="table",
        help="output format ['table', 'csv']")
    session_ls.add_argument(
        "--download",
        dest="download",
        action="store_true",
        help=
        "boolean is true if user would like to download. use --download-path to specify a path"
    )
    session_ls.add_argument(
        "--download-path",
        dest="download_path",
        default=None,
        help=
        "checked only if download is specified. saves output to location specified"
    )

    session_select = session_subcommand_parsers.add_parser(
        "select", help="select a session")
    session_select.add_argument(
        "name_or_id", help="name or id of session to select")

    # Environment
    environment_parser = subparsers.add_parser(
        "environment", help="environment module")
    environment_subcommand_parsers = environment_parser.add_subparsers(
        title="subcommands", dest="subcommand")

    environment_setup = environment_subcommand_parsers.add_parser(
        "setup",
        help=
        "setup environment adds a predefined supported environment into your project environment directory"
    )
    environment_setup.add_argument(
        "--name",
        dest="name",
        default=None,
        type=str,
        help=
        "name of environment to be used for environment (e.g. my-new-environment). if none is given, "
        "a prompt will present the supported names")
    environment_setup.add_argument(
        "--type",
        dest="type",
        default=None,
        type=str,
        help=
        "type of environment to be used for environment (e.g. cpu). if none is given, a prompt "
        "will present the supported type")
    environment_setup.add_argument(
        "--framework",
        dest="framework",
        default=None,
        type=str,
        help=
        "framework (and relevant libraries) to be used for environment (e.g. data-analytics). if none is given, "
        "a prompt will present the supported names")
    environment_setup.add_argument(
        "--language",
        dest="language",
        default=None,
        type=str,
        help=
        "language of environment to be used for environment (e.g. py27). if none is given, a prompt will "
        "present the supported language for the name and type")

    environment_create = environment_subcommand_parsers.add_parser(
        "create",
        help=
        "create environment using the definition paths given, if not looks in your project environment directory, or creates a default"
    )
    environment_create.add_argument(
        "--paths",
        dest="paths",
        default=None,
        action="append",
        type=str,
        help=
        "list of absolute or relative filepaths and/or dirpaths to collect; can specify destination names with '>' (e.g. /path/to/file>hello, /path/to/file2, /path/to/dir>newdir)"
    )
    environment_create.add_argument(
        "--name",
        "-n",
        dest="name",
        default=None,
        help="name given to the environment")
    environment_create.add_argument(
        "--description",
        "-d",
        dest="description",
        default=None,
        help="description of environment")

    environment_update = environment_subcommand_parsers.add_parser(
        "update", help="update an environment by id")
    environment_update.add_argument("id", help="environment id to update")
    environment_update.add_argument(
        "--name", dest="name", help="new name for the environment")
    environment_update.add_argument(
        "--description",
        dest="description",
        help="new description for the environment")

    environment_delete = environment_subcommand_parsers.add_parser(
        "delete", help="delete a environment by id")
    environment_delete.add_argument("id", help="id of environment to delete")

    environment_ls = environment_subcommand_parsers.add_parser(
        "ls", help="list environments")
    environment_ls.add_argument(
        "--format",
        dest="format",
        default="table",
        help="output format ['table', 'csv']")
    environment_ls.add_argument(
        "--download",
        dest="download",
        action="store_true",
        help=
        "boolean is true if user would like to download. use --download-path to specify a path"
    )
    environment_ls.add_argument(
        "--download-path",
        dest="download_path",
        default=None,
        help=
        "checked only if download is specified. saves output to location specified"
    )

    # Snapshot
    snapshot_parser = subparsers.add_parser(
        "snapshot",
        description=__("argparser", "cli.snapshot.description"),
        help="snapshot module")
    snapshot_subcommand_parsers = snapshot_parser.add_subparsers(
        title="subcommands", dest="subcommand")

    snapshot_create = snapshot_subcommand_parsers.add_parser(
        "create",
        description=__("argparser", "cli.snapshot.create.description"),
        help="create a snapshot")
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
        "--run-id",
        dest="run_id",
        default=None,
        help="specify run id to pull information from")

    snapshot_create.add_argument(
        "--environment-id",
        dest="environment_id",
        default=None,
        help="environment id from environment object")
    snapshot_create.add_argument(
        "--environment-paths",
        dest="environment_paths",
        default=None,
        action="append",
        type=str,
        help=
        "list of absolute or relative filepaths and/or dirpaths to collect; can specify destination names with '>' (e.g. /path/to/file>hello, /path/to/file2, /path/to/dir>newdir)"
    )
    # snapshot_create.add_argument(
    #     "--environment-name",
    #     dest="environment_name",
    #     default=None,
    #     help="name given to the environment")
    # snapshot_create.add_argument(
    #     "--environment-description",
    #     dest="environment_description",
    #     default=None,
    #     help="description of environment")

    snapshot_create.add_argument(
        "--paths",
        dest="paths",
        default=None,
        action="append",
        help=
        "list of absolute or relative filepaths and/or dirpaths to collect; can specify destination names with '>' (e.g. /path/to/file>hello, /path/to/file2, /path/to/dir>newdir)"
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
    snapshot_update.add_argument("id", help="snapshot id to update")
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
    snapshot_delete.add_argument("id", help="snapshot id to delete")

    snapshot_ls = snapshot_subcommand_parsers.add_parser(
        "ls", help="list snapshots")
    snapshot_ls.add_argument(
        "--session-id",
        dest="session_id",
        default=None,
        help="session id to filter")
    snapshot_ls.add_argument(
        "--details",
        dest="details",
        action="store_true",
        help="show detailed snapshot information")
    snapshot_ls.add_argument(
        "--all",
        dest="show_all",
        action="store_true",
        help="show all visible and hidden snapshots")
    snapshot_ls.add_argument(
        "--format",
        dest="format",
        default="table",
        help="output format ['table', 'csv']")
    snapshot_ls.add_argument(
        "--download",
        dest="download",
        action="store_true",
        help=
        "boolean is true if user would like to download. use --download-path to specify a path"
    )
    snapshot_ls.add_argument(
        "--download-path",
        dest="download_path",
        default=None,
        help=
        "checked only if download is specified. saves output to location specified"
    )

    snapshot_checkout = snapshot_subcommand_parsers.add_parser(
        "checkout", help="checkout a snapshot by id")
    snapshot_checkout.add_argument("id", help="snapshot id to checkout")

    snapshot_diff = snapshot_subcommand_parsers.add_parser(
        "diff", help="view diff between 2 snapshots")
    snapshot_diff.add_argument("id_1", default=None, help="snapshot id 1")
    snapshot_diff.add_argument("id_2", default=None, help="snapshot id 2")

    snapshot_inspect = snapshot_subcommand_parsers.add_parser(
        "inspect", help="inspect a snapshot by id")
    snapshot_inspect.add_argument("id", default=None, help="snapshot id")

    return parser
