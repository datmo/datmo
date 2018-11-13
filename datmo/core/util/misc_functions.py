#!/usr/bin/python

import os
import re
import ast
import hashlib
import textwrap
import datetime
import pytz
import json
import tzlocal
import pytest
import collections
import platform
import tempfile
import subprocess
import zipfile
import sys
import shutil
import requests
from enum import Enum
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
try:
    basestring
except NameError:
    basestring = str

from glob import glob

from datmo.core.controller.environment.driver.dockerenv import DockerEnvironmentDriver
from datmo.core.util.i18n import get as __
from datmo.core.util.exceptions import (
    PathDoesNotExist, MutuallyExclusiveArguments, RequiredArgumentMissing,
    EnvironmentConnectFailed, EnvironmentExecutionError,
    InvalidDestinationName, TooManyArgumentsFound)


def bytes2human(n):
    # http://code.activestate.com/recipes/578019
    # >>> bytes2human(10000)
    # '9.8K'
    # >>> bytes2human(100001221)
    # '95.4M'
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.1f%s' % (value, s)
    return "%sB" % n


def slack_message(webhook_url, options):
    if webhook_url is None:
        return False

    slack_data = {
        "attachments": [{
            "fallback":
                "Trigger from Datmo",
            "color":
                "warning",
            "pretext":
                "Trigger from Datmo during inference",
            "author_name":
                options.get("author_name"),
            "title":
                options.get("title"),
            "text":
                options.get("text"),
            "fields": [{
                "title":
                    "Priority",
                "value":
                    options.get("priority")
                    if options.get("priority") is not None else "High",
                "short":
                    False
            }],
            "ts":
                options.get("timestamp")
        }]
    }

    response = requests.post(
        webhook_url,
        data=json.dumps(slack_data),
        headers={'Content-Type': 'application/json'})
    if response.status_code != 200:
        return False

    return True


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
            printable_output = printable_output + str(key) + ": " + str(
                value) + "\n"
    return printable_output


def convert_keys_to_string(data):
    if isinstance(data, basestring):
        return str(data)
    elif isinstance(data, collections.Mapping):
        return dict(map(convert_keys_to_string, data.items()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(convert_keys_to_string, data))
    else:
        return data


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


# TODO: add test
def check_docker_inactive(filepath, datmo_directory_name):
    try:
        test = DockerEnvironmentDriver(
            root=filepath, datmo_directory_name=datmo_directory_name)
        test.connect()
        definition_path = os.path.join(filepath, "Dockerfile")
        if platform.system() == "Windows":
            with open(definition_path, "wb") as f:
                f.write(to_bytes("FROM python:3.5-alpine" + "\n"))
                f.write(to_bytes(str("RUN echo hello")))
            test.build("docker-test", definition_path)
        return False
    except (EnvironmentConnectFailed, EnvironmentExecutionError):
        return True


# TODO: add test
def pytest_docker_environment_failed_instantiation(filepath):
    return pytest.mark.skipif(
        # TODO: abstract the "datmo_directory_name"
        check_docker_inactive(filepath, ".datmo"),
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
    data_rows = [len(row) for row in data]
    num_col = max(data_rows) if data_rows else 0
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
        list of file tuples of the form (absolute_source_path, absolute_dest_filepath)
    directories : list
        list of directory tuples of the form (absolute_source_path, absolute_dest_filepath)
    files_rel : list
        list of file tuples of the form (absolute_source_path, relative_dest_path)
    directories_rel : list
        list of directory tuples of the form (absolute_source_path, relative_dest_path)

    Raises
    ------
    InvalidDestinationName
        destination specified in paths is not valid
    PathDoesNotExist
        if the path does not exist
    """
    files, files_rel, directories, directories_rel = [], [], [], []
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
            files_rel.append((src_abs_path, dest_name))
        elif os.path.isdir(src_abs_path):
            directories.append((src_abs_path, dest_abs_path))
            directories_rel.append((src_abs_path, dest_name))
        else:
            raise PathDoesNotExist(src_abs_path)
    return files, directories, files_rel, directories_rel


def get_headers(access_key):
    return {
        'Authorization': str(access_key),
        'Content-type': 'application/json'
    }


def authenticated_get_call(url, access_key=None, stream=False):
    headers = get_headers(access_key)
    res = requests.get(url, headers=headers, stream=stream)
    return res


def authenticated_post_call(url,
                            data,
                            access_key=None,
                            content_type="application/json"):
    headers = get_headers(access_key)
    res = requests.post(url, data=data, headers=headers)
    return res


def authenticated_put_call(url, data, access_key=None):
    headers = get_headers(access_key)
    res = requests.put(url, data=data, headers=headers)
    return res


def authenticated_delete_call(url, access_key=None):
    headers = get_headers(access_key)
    res = requests.delete(url, headers=headers)
    return res


# class for colors
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Commands(object):
    def __init__(self):
        from datmo.core.util.logger import DatmoLogger
        from datmo.config import Config
        self.config = Config()
        self.docker_cli = self.config.docker_cli
        self.log = DatmoLogger.get_logger(__name__)
        self.log.info("handling command %s", self.config.home)

    def run_cmd(self, shell_cmd):
        try:
            if type(shell_cmd) is list:
                p = subprocess.Popen(shell_cmd, stdout=subprocess.PIPE)
                out, e = p.communicate()
                self.log.info("")
                if e:
                    self.log.info(e)
                    self.log.info(
                        bcolors.FAIL + "error while running the command %s" %
                        (shell_cmd))
                else:
                    return {'output': out, 'status': True}
            else:
                process_returncode = subprocess.Popen(
                    shell_cmd, shell=True).wait()
                self.log.info("")
                if process_returncode == 0:
                    return {'status': True}
                else:
                    return {'status': False}
        except Exception as e:
            self.log.info(e)
            self.log.info(bcolors.FAIL + "error while running the command %s" %
                          (shell_cmd))
            return {'status': False}

    def docker_build(self, dockerfile_path=None, project_name=None):
        if dockerfile_path:
            shell_cmd = '%s build -t %s -f %s .' % (self.docker_cli,
                                                    project_name,
                                                    dockerfile_path)
        else:
            shell_cmd = '%s build -t %s .' % (self.docker_cli, project_name)

        self.run_cmd(shell_cmd)

    def docker_tag(self, project_name, old_image_tag, new_image_tag):
        old_image_name_tag = project_name + ':' + old_image_tag
        new_image_name_tag = project_name + ':' + new_image_tag
        shell_cmd = '%s tag %s  %s' % (self.docker_cli, old_image_name_tag,
                                       new_image_name_tag)
        self.run_cmd(shell_cmd)

    def zip_folder(self, folder_path, output_path):
        """Zip the contents of an entire folder (with that folder included
        in the archive). Empty subfolders will be included in the archive
        as well.
        """
        # Retrieve the paths of the folder contents.
        contents = os.walk(folder_path)
        try:
            zip_file = zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED)
            for root, folders, files in contents:
                # Include all subfolders, including empty ones.
                for folder_name in folders:
                    absolute_path = os.path.join(root, folder_name)
                    relative_path = absolute_path.replace(folder_path, '')
                    zip_file.write(absolute_path, relative_path)
                for file_name in files:
                    if file_name != 'datmo_model.zip':
                        absolute_path = os.path.join(root, file_name)
                        relative_path = absolute_path.replace(folder_path, '')
                        zip_file.write(absolute_path, relative_path)
        except IOError as err:
            _, strerror = err.args
            self.log.info(strerror)
            sys.exit(1)
        except OSError as err:
            _, strerror = err.args
            self.log.info(strerror)
            sys.exit(1)
        except zipfile.BadZipfile as err:
            _, strerror = err.args
            self.log.info(strerror)
            sys.exit(1)
        finally:
            zip_file.close()

    def create_datmo_dockerfile(self,
                                dockerfile='Dockerfile',
                                filepath=os.getcwd()):
        """
        in order to create intermediate dockerfile to run
        """

        file_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'src_files')

        # Combine dockerfiles
        destination = open(os.path.join(filepath, 'datmoDockerfile'), 'wb')
        shutil.copyfileobj(
            open(os.path.join(filepath, dockerfile), 'rb'), destination)
        shutil.copyfileobj(
            open(os.path.join(file_dir, 'stubDockerfile'), 'rb'), destination)
        destination.close()

    def copy(self, src, dst, symlinks=False, ignore=None):
        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dst, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, symlinks, ignore)
            else:
                shutil.copy2(s, d)


class Status(Enum):
    SUCCESS = 0
    FAILURE = 1


class Response(object):
    # success by default
    result = {}
    message = 'passed'
    status = 0
