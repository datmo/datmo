"""
Bring in all of Datmo's public python interfaces
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
from datmo.core.util.logger import DatmoLogger
from datmo.config import Config

datmo_root = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(datmo_root, 'VERSION')) as file:
    __version__ = file.read()

# Config is required to run first so it can
# initialize/find datmo home directory (.datmo)
# This is required for logging to place the logs in a
# place for the user.
config = Config()
config.set_home(os.getcwd())

log = DatmoLogger.get_logger(__name__)
log.info("handling command %s", config.home)

import datmo.snapshot
import datmo.logger
import datmo.config
import datmo.monitoring
