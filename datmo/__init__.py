"""
Bring in all of Datmo's public python interfaces
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os

datmo_root = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(datmo_root, 'VERSION')) as file:
    __version__ = file.read()

import datmo.snapshot
import datmo.task
import datmo.config
