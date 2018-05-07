#!/usr/bin/python

import os
import re
import hashlib
import textwrap
import datetime
from io import open
try:
    to_unicode = unicode
except NameError:
    to_unicode = str
from glob import glob

from datmo.core.util.i18n import get as __
from datmo.core.util.exceptions import (PathDoesNotExist,
                                        MutuallyExclusiveArguments)


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


def printable_string(string, max_width=100):
    return '\n'.join(textwrap.wrap(string, max_width))


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


def get_filehash(filepath):
    if not os.path.isfile(filepath):
        raise PathDoesNotExist(
            __("error", "util.misc_functions.get_filehash", filepath))
    BUFF_SIZE = 65536
    sha1 = hashlib.md5()
    with open(filepath, "rb") as f:
        while True:
            data = f.read(BUFF_SIZE)
            if not data:
                break
            sha1.update(data)
    return sha1.hexdigest()


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


def mutually_exclusive(mutually_exclusive_args, arguments_dictionary,
                       dictionary):
    mutually_exclusive_arg_count = 0
    for arg in mutually_exclusive_args:
        if arg in arguments_dictionary and arguments_dictionary[arg] is not None:
            dictionary[arg] = arguments_dictionary[arg]
            mutually_exclusive_arg_count += 1
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
