#!/usr/bin/python

import os
import re
import ast
import hashlib
import textwrap
import datetime
import pytz
import tzlocal
import pytest
import platform
import tempfile
from io import open
try:
    to_unicode = unicode
except NameError:
    to_unicode = str
try:

    def to_bytes(val):
        return bytes(val)

    to_bytes("test")
except TypeError:

    def to_bytes(val):
        return bytes(val, "utf-8")

    to_bytes("test")
from glob import glob

from datmo.core.controller.environment.driver.dockerenv import DockerEnvironmentDriver
from datmo.core.util.i18n import get as __
from datmo.core.util.exceptions import (
    PathDoesNotExist, MutuallyExclusiveArguments, RequiredArgumentMissing,
    EnvironmentInitFailed, EnvironmentExecutionError, InvalidDestinationName,
    TooManyArgumentsFound)


def grep(pattern, fileObj):
    r = []
    linenumber = 0
    for line in fileObj:
        linenumber += 1
        if re.search(pattern, line):
            r.append((linenumber, line))
    return r


def printable_dict(input_dictionary):
    printable_output = ""
    if input_dictionary:
        for key, value in input_dictionary.items():
            printable_output = printable_output + key + ": " + str(value) + "\n"
    return printable_output


def printable_object(object, max_width=40):
    if not object:
        return ""
    if isinstance(object, str):
        printable_str = object
    elif isinstance(object, dict):
        printable_str = printable_dict(object)
    else:
        printable_str = str(object)
    return '\n'.join(textwrap.wrap(printable_str, max_width))


def which(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file
    return None


def get_nvidia_devices():
    nvidia_devices = glob('/dev/nvidia*')
    devices = []
    for device in nvidia_devices:
        devices.append(device + ':' + device + ':rwm')
    return devices


def create_unique_hash(base_hash=None, salt=None):
    if not salt:
        salt = os.urandom(16)
    else:
        salt = salt.encode('utf-8')
    if not base_hash:
        sha1 = hashlib.sha1()
    else:
        sha1 = hashlib.sha1(base_hash)
    timestamp_microsec = (
        datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)
    ).total_seconds() * 100000
    sha1.update(salt + str(timestamp_microsec).encode('utf-8'))
    return sha1.hexdigest()


def mutually_exclusive(mutually_exclusive_args, input_dictionary,
                       output_dictionary):
    """
    Goes through args to check for to see if they exist in the input_dictionary
    and adds them to output_dictionary. The output_dictionary
    is mutated in the function. This function will raise errors if at least
    one of the arguments is not present or more than 1

    Parameters
    ----------
    mutually_exclusive_args : list
        arg names to search for in input dictionary
    input_dictionary : dict
        input dictionary of arguments and values to search through
    output_dictionary : dict
        output dictionary

    Raises
    ------
    MutuallyExclusiveArguments
    RequiredArgumentMissing
    """
    mutually_exclusive_arg_count = 0
    for arg in mutually_exclusive_args:
        if input_dictionary.get(arg, None):
            output_dictionary[arg] = input_dictionary[arg]
            mutually_exclusive_arg_count += 1
    if mutually_exclusive_arg_count == 0 and len(mutually_exclusive_args) > 0:
        raise RequiredArgumentMissing()
    if mutually_exclusive_arg_count > 1:
        raise MutuallyExclusiveArguments(
            __("error", "util.misc_functions.mutually_exclusive",
               ' '.join(mutually_exclusive_args)))
    return


def find_project_dir(starting_path=os.getcwd()):
    if starting_path == "/":
        raise Exception("project not found")

    if os.path.expanduser("~") == starting_path:
        raise Exception("project not found")

    if is_project_dir(starting_path):
        return starting_path
    else:
        # Remove last dir, walking down the tree, testing each dir
        # os.path.split creates a tuple of the basepath and last directory
        # take the first part
        return find_project_dir(os.path.split(starting_path)[0])


def parameterized(dec):
    """Lifted from https://stackoverflow.com/questions/5929107/decorators-with-parameters

    Parameters
    ----------
    dec : function

    Returns
    -------
    function
    """

    def layer(*args, **kwargs):
        def repl(f):
            return dec(f, *args, **kwargs)

        return repl

    return layer


def is_project_dir(path):
    return ".datmo" in os.listdir(path) and os.path.isdir(
        os.path.join(path, ".datmo"))


def check_docker_inactive(filepath):
    try:
        test = DockerEnvironmentDriver(filepath=filepath)
        test.init()
        definition_path = os.path.join(filepath, "Dockerfile")
        if platform.system() == "Windows":
            with open(definition_path, "wb") as f:
                f.write(to_bytes("FROM python:3.5-alpine" + "\n"))
                f.write(to_bytes(str("RUN echo hello")))
            test.build("docker-test", definition_path)
        return False
    except (EnvironmentInitFailed, EnvironmentExecutionError):
        return True


def pytest_docker_environment_failed_instantiation(filepath):
    return pytest.mark.skipif(
        check_docker_inactive(filepath),
        reason="a running environment could not be instantiated")


def parse_cli_key_value(cli_string, default_key):
    dictionary = {}
    # parse string for json blob
    try:
        item_dict = ast.literal_eval(cli_string)
        parsed_dict = True
        for item_key, item_value in item_dict.items():
            dictionary[item_key] = item_value.strip()
    except:
        parsed_dict = False

    cli_string_split = cli_string.split(":")
    if not parsed_dict and len(cli_string_split) == 2:
        item_key, item_value = cli_string_split
        dictionary[item_key.strip()] = item_value.strip()
    elif not parsed_dict:
        dictionary[default_key] = cli_string.strip()

    return dictionary


def prettify_datetime(datetime_obj, tz=None):
    if not tz:
        tz = tzlocal.get_localzone()
    return str(
        datetime_obj.replace(tzinfo=pytz.utc).astimezone(tz=tz)
        .strftime("%a %b %d %H:%M:%S %Y %z"))


def format_table(data, padding=2):
    num_col = max(len(row) for row in data)
    col_widths = []
    for i in range(num_col):
        col_width = max(len(row[i]) for row in data) + padding
        col_widths.append(col_width)
    table_str = ""
    for row in data:
        table_str = table_str + "".join(
            word.ljust(col_widths[idx]) for idx, word in enumerate(row)) + "\n"
    return table_str


def list_all_filepaths(absolute_dirpath):
    """Returns all filepaths within dir relative to dir root"""
    return [
        os.path.relpath(os.path.join(dirpath, file), absolute_dirpath)
        for (dirpath, dirnames, filenames) in os.walk(absolute_dirpath)
        for file in filenames
    ]


def get_datmo_temp_path(filepath):
    # Create temp directory within .datmo/tmp
    datmo_temp_path = os.path.join(filepath, ".datmo", "tmp")
    if not os.path.exists(datmo_temp_path):
        os.makedirs(datmo_temp_path)
    return tempfile.mkdtemp(dir=datmo_temp_path)


def parse_path(path):
    """Parse user given path

    Parameters
    ----------
    path : str
        user given path

    Returns
    -------
    src_path : str
        user given source path
    dest_name : str
        user given destination name

    Raises
    ------
    InvalidDestinationName
        if destination name is a path then error
    """
    # Parse given path and split out the destination
    path = path.strip()
    path_split_list = path.split(">")
    if len(path_split_list) == 1:
        src_path = path_split_list[0]
        src_dir, src_name = os.path.split(src_path)
        dest_name = src_name
    elif len(path_split_list) == 2:
        src_path, dest_name = path_split_list
    else:
        raise TooManyArgumentsFound()
    # Test dest_path to ensure it is valid
    if os.path.isabs(dest_name):
        raise InvalidDestinationName()
    return src_path, dest_name


def parse_paths(default_src_prefix, paths, dest_prefix):
    """Parse user given paths. Checks only source paths and destination are valid

    Parameters
    ----------
    default_src_prefix : str
        default directory prefix to append if source path is not an absolute path
    paths : list
        list of absolute or relative filepaths and/or dirpaths to collect with destination names
        (e.g. "/path/to/file>hello", "/path/to/file2", "/path/to/dir>newdir")
    dest_prefix : str
        destination directory prefix to append to the destination filename

    Returns
    -------
    files : list
        list of tuples of the form (absolute_source_path, absolute_dest_filepath)
    directories : list
        list of tuples of the form (absolute_source_path, absolute_dest_filepath)

    Raises
    ------
    InvalidDestinationName
        destination specified in paths is not valid
    PathDoesNotExist
        if the path does not exist
    """
    files = []
    directories = []
    for path in paths:
        src_path, dest_name = parse_path(path)
        # For dest_name, append the dest_prefix
        dest_abs_path = os.path.join(dest_prefix, dest_name)
        # For src_path if not absolute, append the default src_prefix
        if not os.path.isabs(path):
            src_abs_path = os.path.join(default_src_prefix, src_path)
        else:
            src_abs_path = src_path
        # Check if source is file or directory and save accordingly
        if os.path.isfile(src_abs_path):
            files.append((src_abs_path, dest_abs_path))
        elif os.path.isdir(src_abs_path):
            directories.append((src_abs_path, dest_abs_path))
        else:
            raise PathDoesNotExist(src_abs_path)
    return files, directories
