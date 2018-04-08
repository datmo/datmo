import os
import hashlib
import logging
import textwrap
from glob import glob

from datmo.util.i18n import get as _
from datmo.util.exceptions import DoesNotExistException


def printable_dict(input_dictionary):
    printable_output = ""
    if input_dictionary:
        for key, value in input_dictionary.items():
            printable_output = printable_output + key + ": " + str(value) + "\n"
    return printable_output

def printable_string(string, max_width=100):
    return '\n'.join(textwrap.wrap(string, max_width))

def which(program):
    import os
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
        raise DoesNotExistException(_("error",
                                      "util.misc_functions.get_filehash",
                                      filepath))
    BUFF_SIZE = 65536
    sha1 = hashlib.md5()
    with open(filepath, "rb") as f:
        while True:
            data = f.read(BUFF_SIZE)
            if not data:
                break
            sha1.update(data)
    return sha1.hexdigest()