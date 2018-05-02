"""
TODO: Pull correct lang file based on locale of system.  Hardcoded to use 'en' for now
"""
import importlib


def get_lang(locale='en'):
    module = importlib.import_module('datmo.core.util.lang.' + locale)
    return getattr(module, 'get_messages')()
