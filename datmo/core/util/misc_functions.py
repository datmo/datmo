import os
import hashlib
import logging
import textwrap
import datetime
from io import open
try:
    to_unicode = unicode
except NameError:
    to_unicode = str
from glob import glob

from datmo.core.util.i18n import get as __
from datmo.core.util.exceptions import PathDoesNotExist, \
    MutuallyExclusiveArguments


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


def create_logger(logfile_location):
    logger = logging.getLogger('datmo')
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(logfile_location)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


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
